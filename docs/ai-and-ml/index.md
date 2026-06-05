# GPU Computing on Juno

Juno provides several GPU partitions suited to different workloads, from interactive prototyping to large-scale distributed AI training. This section covers how to set up a GPU environment, select the right partition, and run jobs efficiently.

---

## GPU Partitions

| Partition | Nodes | GPUs / Node | GPU Model | VRAM / GPU | Time Limit | Best For |
|---|---|---|---|---|---|---|
| `a30` | 2 | 2 | NVIDIA A30 | 24 GB | 2 days | Medium GPU workloads, inference, development |
| `a30-2.12gb` | 1 | 4 (virtual, half-A30) | NVIDIA A30 | 12 GB | 2 days | Multiple concurrent small jobs |
| `a30-4.6gb` | 1 | 8 (virtual, quarter-A30) | NVIDIA A30 | 6 GB | 2 days | Light GPU jobs, debugging |
| `h100` | 1 | 4 | NVIDIA H100 (80GB HBM3) | 80 GB | 2 days | Large models, high-throughput / multi-GPU training |
| `h100-94gb` | 1 | 1 | NVIDIA H100 NVL | 94 GB | 2 days | Single high-memory GPU jobs |
| `h100-2.47gb` | 1 | 4 (virtual, half-H100) | NVIDIA H100 | 47 GB | 2 days | Concurrent moderate-memory GPU jobs |
| `h200` *(coming soon)* | 26 | 2 | NVIDIA H200 NVL | 141 GB | 2 days | Very large models, distributed AI training |

!!! warning "Coming soon: H200 Nodes (expected June 2026)"
    Juno is adding 26 H200 nodes (52 GPUs total). The NVIDIA H200 NVL carries **141 GB of HBM3e memory** — nearly double the H100 — making it ideal for training and serving large language models that don't fit on older GPUs. These are **NVL cards with no NVLink** between GPUs: GPUs attach via PCIe Gen 5.0, and nodes are connected by 400 Gb InfiniBand for distributed training.

    **These nodes are not yet available.** The `h200` partition does not exist until the rollout completes — jobs submitted to it will fail. Until then, use the `h100` partition for large-GPU work. This page is documented ahead of time so it's ready when the nodes go live.

---

## Setting Up a GPU Environment

The recommended approach on Juno is to create a Conda environment with the GPU libraries you need.

### 1. Load the necessary modules

```bash
module purge
module load gnu14
module load miniconda
module load cuda/12.6
```

!!! note
    Use `cuda/12.6` for H100 and H200 nodes. Use `cuda/12.4` for A30 nodes. Check compatibility with `nvcc --version` after loading.

### 2. Create a Conda environment

```bash
conda create -n gpu-env python=3.11 -y
conda activate gpu-env
```

### 3. Install PyTorch with CUDA support

```bash
# PyTorch with CUDA 12.6
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

Check that PyTorch sees the GPU after loading your environment on a compute node:

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

### 4. Install other GPU libraries

```bash
# CuPy — GPU-accelerated NumPy-compatible arrays
pip install cupy-cuda12x

# Numba — JIT compilation for GPU kernels
pip install numba

# vLLM — high-throughput LLM inference
pip install vllm
```

See the [Miniconda Guide](../advanced/miniconda.md) for more on managing Conda environments on Juno.

---

## Checking GPU Availability Before Submitting

```bash
# See GPU partition status
sinfo -p h100,h100-94gb,h100-2.47gb,a30,a30-2.12gb,a30-4.6gb

# Detailed view of a specific GPU node
scontrol show node g-05-01
```

Key fields to look for in `scontrol show node`:

- `Gres` — which GPUs are present and their count
- `AllocTRES` vs `CfgTRES` — how many GPUs are currently allocated vs. available
- `State` — `MIXED` means some GPUs are free

```bash
# See how many GPUs are free on each node
sinfo -p h100 -o "%.10N %.8t %.10G"
```

---

## Quick Sanity Check Job

Before submitting a long training run, verify your environment works with a short test job:

```bash
#!/bin/bash
#SBATCH -J gpu-test
#SBATCH -o gpu_test_%j.out
#SBATCH -p h100
#SBATCH -N 1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16GB
#SBATCH -t 0:05:00

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

python - <<'EOF'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
for i in range(torch.cuda.device_count()):
    props = torch.cuda.get_device_properties(i)
    print(f"  GPU {i}: {props.name} — {props.total_memory / 1e9:.1f} GB")

# Quick compute test
x = torch.randn(4096, 4096, device='cuda')
y = x @ x.T
print(f"Matrix multiply OK — result shape: {y.shape}")
EOF
```

---

## What's in This Section

- [PyTorch Training Jobs](pytorch-training.md) — single-GPU, multi-GPU DDP, and multi-node distributed training
- [GPU Performance & Monitoring](gpu-performance.md) — profiling, mixed precision, memory optimization
- [AlphaFold 3](alphafold3.md) — protein structure prediction using the shared container and databases

---

## Related Pages

- [Available Software](../working-on-juno/software.md) — full list of GPU-related modules
- [SLURM Job Scheduler](../running-programs/slurm.md) — job scripts, partitions, and scheduling
- [Miniconda](../advanced/miniconda.md) — managing Python environments
- [Containers](../advanced/containers.md) — running containerized GPU workloads (e.g., ColabFold, Stable Diffusion)
