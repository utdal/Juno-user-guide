# GPU Performance & Monitoring

## Overview

This page covers tools and techniques for measuring, profiling, and improving GPU job performance on Juno.

---

## Real-Time GPU Monitoring — `nvidia-smi`

### Watching a running job

SSH to a node allocated to your job, then run:

```bash
# Watch GPU stats every 2 seconds
watch -n 2 nvidia-smi

# Compact format showing only the most useful fields
nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.free,temperature.gpu \
           --format=csv -l 2
```

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.86.15              Driver Version: 570.86.15      CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 80GB HBM3         On   |   00000000:17:00.0 Off |                    0 |
| N/A   38C    P0            104W / 700W  |   24576MiB /  81920MiB |     87%      Default |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA H100 80GB HBM3         On   |   00000000:31:00.0 Off |                    0 |
| N/A   41C    P0             98W / 700W  |   24576MiB /  81920MiB |     85%      Default |
+-----------------------------------------+------------------------+----------------------+
|   2  NVIDIA H100 80GB HBM3         On   |   00000000:B1:00.0 Off |                    0 |
| N/A   37C    P0            110W / 700W  |   24576MiB /  81920MiB |     92%      Default |
+-----------------------------------------+------------------------+----------------------+
|   3  NVIDIA H100 80GB HBM3         On   |   00000000:CA:00.0 Off |                    0 |
| N/A   39C    P0            101W / 700W  |   24576MiB /  81920MiB |     88%      Default |
+-----------------------------------------+------------------------+----------------------+
```

**What to look for:**

| Metric | Healthy range | If low... |
|---|---|---|
| GPU utilization (`Volatile GPU-Util`) | > 80% | Data loading is the bottleneck — increase `num_workers` or use `pin_memory=True` |
| GPU memory usage | 60–90% of total | Increase `batch_size` to improve throughput |
| SM utilization | > 70% | Kernels may be poorly optimized or model is too small for this GPU |
| Temperature | < 85°C | Normal; Juno nodes have active cooling |

### From inside a job script

Add these diagnostics to your SLURM script to capture GPU state in the log:

```bash
# Log GPU info at job start
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
nvidia-smi topo -m    # show GPU interconnect topology (NVLink, PCIe)
```

---

## Post-Job Efficiency Report — `jobstats`

After your job finishes, `jobstats` gives a summary of CPU and GPU utilization:

```bash
module load jobstats
jobstats $JOBID
```

The output shows:

- **CPU utilization** — should be close to 100% for CPU-bound preprocessing; lower is fine if the GPU is the bottleneck
- **CPU memory usage** — if you used only 40% of requested memory, request less next time to improve queue times
- **GPU utilization** — printed when GPU resources are tracked
- **Run Time vs. Time Limit** — if you used < 50% of requested time, shorten `--time` in future jobs

See [Monitoring Jobs and Cluster State](../running-programs/advanced-slurm.md) for a full walkthrough of `jobstats` output.

---

## Automatic Mixed Precision (AMP)

By default, PyTorch uses 32-bit floats (`float32`). Switching to 16-bit (`bfloat16` or `float16`) for most operations roughly doubles throughput and halves memory usage on modern GPUs, with minimal accuracy impact.

H100 and H200 GPUs have dedicated **Tensor Cores** that accelerate `bfloat16` and `float16` matrix operations — this is where the biggest speedup comes from.

### Enabling AMP in your training loop

```python
from torch.cuda.amp import GradScaler, autocast

scaler = GradScaler()   # handles gradient scaling for float16 stability

for images, labels in train_loader:
    images, labels = images.to(device), labels.to(device)
    optimizer.zero_grad()

    with autocast(dtype=torch.bfloat16):   # or torch.float16
        outputs = model(images)
        loss = criterion(outputs, labels)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

!!! tip "bfloat16 vs float16"
    Prefer `bfloat16` on H100 and H200 GPUs — it has the same dynamic range as `float32` so it rarely needs gradient scaling. Use `float16` only on older GPUs (A30, A100) that don't support `bfloat16` natively.

### Expected impact

| Precision | Throughput | VRAM usage | Accuracy |
|---|---|---|---|
| float32 (default) | 1× | 1× | Full |
| float16 with AMP | ~1.8× | ~0.6× | Minimal loss |
| bfloat16 with AMP | ~1.8× | ~0.6× | Minimal loss, more stable |

---

## Data Loading Optimization

The GPU can only be as fast as the data pipeline feeding it. A GPU sitting at < 80% utilization usually means the CPU is not loading data fast enough.

```python
DataLoader(
    dataset,
    batch_size=256,
    num_workers=8,        # one worker per CPU core assigned to the job
    pin_memory=True,      # pin memory for faster CPU→GPU transfer
    persistent_workers=True,   # keeps worker processes alive between epochs
    prefetch_factor=2,    # prefetch 2 batches per worker
)
```

**Rule of thumb:** set `num_workers` equal to `--cpus-per-task` in your SLURM script. Increase `--cpus-per-task` if the GPU is still starved.

---

## Profiling with NVIDIA Nsight Systems

For deep performance analysis — identifying exactly which operations are slow, where GPU is idle, and where memory bottlenecks are:

```bash
# Profile 2 epochs and save a report
nsys profile \
    --output profiles/train_%q{SLURM_JOBID} \
    --trace cuda,nvtx,osrt \
    python train.py --epochs 2
```

Add NVTX annotations in your Python code to label regions in the timeline:

```python
import torch.cuda.nvtx as nvtx

for images, labels in train_loader:
    nvtx.range_push("data_transfer")
    images, labels = images.to(device), labels.to(device)
    nvtx.range_pop()

    nvtx.range_push("forward")
    outputs = model(images)
    nvtx.range_pop()

    nvtx.range_push("backward")
    loss.backward()
    nvtx.range_pop()
```

Open the `.nsys-rep` file in NVIDIA Nsight Systems GUI (available via [code-server](../gui-and-tools/vscode.md) or downloaded to your local machine) to visualize the timeline.

---

## GPU Memory Optimization

### Check peak memory usage in your script

```python
print(f"Peak GPU memory: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
torch.cuda.reset_peak_memory_stats()   # reset before next measurement
```

### Techniques to reduce memory usage

**Gradient checkpointing** — trades compute for memory by recomputing activations during backward pass instead of storing them:

```python
from torch.utils.checkpoint import checkpoint

class MyModel(nn.Module):
    def forward(self, x):
        return checkpoint(self.expensive_layer, x)
```

**Accumulate gradients** — simulate a larger effective batch size without holding more activations in memory:

```python
accumulation_steps = 4   # effective batch = batch_size × accumulation_steps

optimizer.zero_grad()
for i, (images, labels) in enumerate(train_loader):
    loss = criterion(model(images.to(device)), labels.to(device))
    (loss / accumulation_steps).backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**`torch.compile`** — compiles the model with kernel fusion, reducing memory traffic (PyTorch 2.0+):

```python
model = torch.compile(model)   # add before the training loop
```

The first forward pass is slower (compilation), but subsequent passes are faster.

---

## Common Performance Issues

### GPU utilization stuck at < 50%

**Likely cause:** Data loading bottleneck.

```bash
# Profile the DataLoader in isolation
python -c "
import time
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

loader = DataLoader(datasets.CIFAR10('.', download=True,
    transform=transforms.ToTensor()), batch_size=256, num_workers=8)
t = time.time()
for i, batch in enumerate(loader):
    if i == 20: break
print(f'{20 / (time.time()-t):.1f} batches/sec')
"
```

If this is slow, increase `num_workers` and `--cpus-per-task` in your SLURM script.

### CUDA out of memory (OOM)

**Diagnosis:**

```bash
# Check exit code — OOM usually appears as signal 9
sacct -j $JOBID --format=JobID,State,ExitCode
```

**Fixes (try in order):**

1. Reduce `batch_size` by half
2. Enable AMP (`bfloat16`) to halve activation memory
3. Enable gradient checkpointing
4. Use gradient accumulation (keep batch_size small, accumulate steps)
5. Switch to a partition with more VRAM (e.g., `h100` (80 GB) or the higher-VRAM `h200` (141 GB) instead of `a30` (24 GB))

### DDP job hangs at startup

The processes are waiting for all ranks to join the process group. Check:

```bash
# Is the MASTER_ADDR set correctly?
scontrol show job $JOBID | grep NodeList

# Is MASTER_PORT open? (firewall or port conflict)
# Try a different port:
export MASTER_PORT=29600
```

Set `NCCL_DEBUG=INFO` in your script to see exactly which transport NCCL is trying to use.

### DDP job hangs mid-training

Processes are stuck waiting for a collective operation (`AllReduce`, `barrier`). Common causes:

- One rank crashed silently — check all per-rank log files
- Uneven number of samples across ranks (ensure `DistributedSampler` is used and `drop_last=True` if needed)
- Timeout: `NCCL_TIMEOUT` defaults to 10 minutes — increase for very slow steps:

```bash
export NCCL_TIMEOUT=1800   # 30 minutes, in seconds
```

---

## GPU-Accelerated Python Libraries

Beyond PyTorch, these libraries let you use GPU acceleration in scientific Python workflows:

### CuPy — GPU NumPy

Drop-in replacement for NumPy operations that runs on GPU:

```python
import cupy as cp

# Same API as NumPy, but runs on GPU
x = cp.random.randn(10_000_000)
result = cp.fft.fft(x)        # GPU FFT
cp.cuda.Device().synchronize() # wait for GPU to finish
print(cp.asnumpy(result[:5]))  # transfer back to CPU
```

```bash
pip install cupy-cuda12x
```

### Numba — GPU Kernels in Python

Write custom CUDA kernels in Python using the `@cuda.jit` decorator:

```python
from numba import cuda
import numpy as np

@cuda.jit
def add_vectors(a, b, c):
    i = cuda.grid(1)
    if i < a.shape[0]:
        c[i] = a[i] + b[i]

n = 1_000_000
a = cuda.to_device(np.random.rand(n))
b = cuda.to_device(np.random.rand(n))
c = cuda.device_array(n)

threads = 256
blocks = (n + threads - 1) // threads
add_vectors[blocks, threads](a, b, c)
cuda.synchronize()
```

```bash
pip install numba
```

### vLLM — LLM Inference

High-throughput inference engine for large language models. Takes advantage of H100/H200 Tensor Cores and PagedAttention for efficient KV-cache management:

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8B", tensor_parallel_size=2)
params = SamplingParams(temperature=0.8, max_tokens=256)

outputs = llm.generate(["Explain gradient descent in simple terms:"], params)
print(outputs[0].outputs[0].text)
```

```bash
pip install vllm
export HF_HOME=~/scratch/hf_cache   # cache models in scratch
```

Use `tensor_parallel_size=N` to split a model across N GPUs when it doesn't fit on one.

---

## Workshop Materials

The HPC@UTD *Accelerating Python with GPUs* workshop covers CuPy, Numba, and PyTorch DDP hands-on exercises with solution keys:

```bash
git clone https://gitlab.circ.utdallas.edu/hpc-utd/workshop/accelerating-python-with-gpus-spring-2026.git
```

The repository includes benchmarked examples comparing NumPy vs. CuPy vs. Numba for common operations (FFT, matrix multiplication, Jacobi solvers), as well as complete DDP training exercises.

---

## Related Pages

- [GPU Computing on Juno](index.md) — GPU partitions and environment setup
- [PyTorch Training Tutorial](pytorch-training.md) — tested single-GPU, multi-GPU DDP, and multi-node example with NCCL explained
- [Monitoring Jobs and Cluster State](../running-programs/advanced-slurm.md) — `jobstats`, `sacct`, `scontrol`
- [Containers](../advanced/containers.md) — running GPU workloads in Apptainer containers
