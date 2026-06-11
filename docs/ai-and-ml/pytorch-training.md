# PyTorch Training Jobs

This page covers three GPU training patterns, from a single GPU to many nodes. Each section includes a complete, ready-to-submit SLURM script and a working training script.

---

## Prerequisites

- A Conda environment with PyTorch installed. See [GPU Computing on Juno](index.md) for setup instructions.
- Familiarity with SLURM job submission. See [SLURM Job Scheduler](../running-programs/slurm.md).

The training scripts on this page use ResNet-18 on CIFAR-10 as a concrete, reproducible example. Replace the model, dataset, and loss function with your own.

---

## Single GPU Training

The simplest case: one job, one GPU.

### SLURM script

```bash
#!/bin/bash
#SBATCH -J train_single_gpu
#SBATCH -o logs/train_%j.out
#SBATCH -e logs/train_%j.err
#SBATCH -p h100                  # or a30 (h200 coming soon)
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8        # feed the DataLoader with enough CPU workers
#SBATCH --mem=64GB
#SBATCH -t 4:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

srun python train_single.py \
    --epochs 20 \
    --batch_size 256 \
    --lr 0.1 \
    --output_dir ./results
```

### Training script — `train_single.py`

```python
#!/usr/bin/env python3
import argparse, json, time
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

def get_dataloaders(batch_size, num_workers=8):
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    transform_val = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    train_set = datasets.CIFAR10('./data', train=True,  download=True, transform=transform_train)
    val_set   = datasets.CIFAR10('./data', train=False, download=True, transform=transform_val)
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=True)
    val_loader   = DataLoader(val_set,   batch_size=batch_size, shuffle=False,
                              num_workers=num_workers, pin_memory=True)
    return train_loader, val_loader

def build_model(num_classes=10):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, num_classes)
    return model

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, total_samples = 0.0, 0
    t0 = time.time()
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        total_samples += images.size(0)
    elapsed = time.time() - t0
    return total_loss / total_samples, total_samples / elapsed

def validate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            _, predicted = torch.max(model(images), 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    return 100.0 * correct / total

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs',     type=int,   default=20)
    parser.add_argument('--batch_size', type=int,   default=256)
    parser.add_argument('--lr',         type=float, default=0.1)
    parser.add_argument('--output_dir', type=str,   default='./results')
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device} — {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    model     = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    train_loader, val_loader = get_dataloaders(args.batch_size)

    history = []
    for epoch in range(1, args.epochs + 1):
        loss, throughput = train_epoch(model, train_loader, criterion, optimizer, device)
        accuracy = validate(model, val_loader, device)
        scheduler.step()
        history.append({'epoch': epoch, 'loss': loss,
                        'accuracy': accuracy, 'throughput': throughput})
        print(f"Epoch {epoch:3d} | loss {loss:.4f} | acc {accuracy:.2f}% "
              f"| {throughput:.0f} samples/sec")

    torch.save(model.state_dict(), f'{args.output_dir}/model.pt')
    with open(f'{args.output_dir}/results.json', 'w') as f:
        json.dump(history, f, indent=2)

if __name__ == '__main__':
    main()
```

### Key options to tune

| Option | Guideline |
|---|---|
| `--gres=gpu:1` | Start with one GPU; add more only if it's actually too slow |
| `--cpus-per-task` | Set to 4–8; each CPU worker prefetches batches while the GPU trains |
| `--mem` | A safe rule: 4× the GPU VRAM (e.g., 64 GB for a 16 GB GPU) |
| `batch_size` | Larger batches use more GPU memory but increase throughput; start at 128–256 |

---

## Multi-GPU Training on One Node (PyTorch DDP)

PyTorch's `DistributedDataParallel` (DDP) is the standard approach for using multiple GPUs. Each GPU runs a full copy of the model; gradients are synchronized across all GPUs after each backward pass via `AllReduce`.

```
  Each GPU holds a full model copy and processes a different data shard:

   GPU 0           GPU 1           GPU 2           GPU 3
  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
  │ model (=) │   │ model (=) │   │ model (=) │   │ model (=) │
  │           │   │           │   │           │   │           │
  │  batch 0  │   │  batch 1  │   │  batch 2  │   │  batch 3  │
  │     ▼     │   │     ▼     │   │     ▼     │   │     ▼     │
  │  grad_0   │   │  grad_1   │   │  grad_2   │   │  grad_3   │
  └─────┬─────┘   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
        │               │               │               │
        └───────────────┴───────┬───────┴───────────────┘
                                │
                    AllReduce: avg(grad_0 … grad_3)
                    via NCCL over NVLink / PCIe
                                │
        ┌───────────────┬───────┴───────┬───────────────┐
        ▼               ▼               ▼               ▼
   optimizer       optimizer       optimizer       optimizer
   step GPU 0      step GPU 1      step GPU 2      step GPU 3

  All four model copies receive identical averaged gradients → stay in sync.
```

!!! tip "DDP vs. DataParallel"
    Use DDP, not the older `DataParallel`. DDP runs each GPU in its own process (no GIL bottleneck), uses efficient NCCL `AllReduce` for gradient sync, and scales to multiple nodes.

!!! note "When does NVLink matter? Target `g-04-02` for communication-heavy jobs"
    NVLink gives roughly **10× the GPU-to-GPU bandwidth** of PCIe, but it only helps jobs bottlenecked on **inter-GPU communication within a node**. On Juno, only `g-04-02` (the 4× H100 node) has NVLink — requesting all 4 GPUs (`-p h100 --gres=gpu:4`, as in the script above) lands you there.

    **Benefits most** (worth targeting `g-04-02`): tensor-parallel LLM serving or training (e.g. vLLM `tensor_parallel_size>1`), FSDP / ZeRO-3, and large-model DDP where gradient sync dominates step time.

    **Barely benefits** (any GPU node is fine): single-GPU jobs, independent per-GPU work (hyperparameter sweeps, array jobs), and compute-bound training with small models or heavy gradient accumulation.

    Inter-node traffic always travels over InfiniBand, so NVLink only ever applies to single-node, multi-GPU jobs.

### Scaling rule
When you multiply the number of GPUs by N, multiply the learning rate by N as well (the *linear scaling rule*). Batch size per GPU stays the same, so effective batch size scales with GPU count.

### SLURM script

```bash
#!/bin/bash
#SBATCH -J train_ddp_1node
#SBATCH -o logs/ddp_1node_%j.out
#SBATCH -e logs/ddp_1node_%j.err
#SBATCH -p h100                  # 4 GPUs per node
#SBATCH -N 1
#SBATCH --ntasks-per-node=4      # one process per GPU
#SBATCH --gres=gpu:4             # request all 4 GPUs on the node
#SBATCH --cpus-per-task=8
#SBATCH --mem=256GB
#SBATCH -t 4:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

# Required for DDP process group initialization
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=29500

export NCCL_IB_DISABLE=1     # single node — no InfiniBand needed
# Note: the 4× H100 node (g-04-02) has NVLink, so leave peer-to-peer ENABLED
# for fast GPU-to-GPU communication. Only set NCCL_P2P_DISABLE=1 on multi-GPU
# nodes WITHOUT NVLink (the 94 GB H100 NVL and A30 nodes — see below).

srun python train_ddp.py \
    --epochs 20 \
    --batch_size 128 \
    --lr 0.1 \
    --output_dir ./results
```

!!! note "ntasks-per-node = number of GPUs"
    SLURM launches one process per task. DDP needs exactly one process per GPU, so `--ntasks-per-node` must equal the number of GPUs you request with `--gres=gpu:N`.

### Training script — `train_ddp.py`

This script works for both single-node multi-GPU and multi-node distributed training (see the next section). It reads the process rank and world size directly from SLURM environment variables.

```python
#!/usr/bin/env python3
"""
PyTorch DDP training script.
Works for single-node multi-GPU and multi-node setups.
Launch with: srun python train_ddp.py [args]
"""
import os
import argparse
import json
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms, models


def setup():
    """Initialize NCCL process group from SLURM environment."""
    rank       = int(os.environ['SLURM_PROCID'])
    world_size = int(os.environ['SLURM_NTASKS'])
    local_rank = int(os.environ['SLURM_LOCALID'])

    dist.init_process_group(
        backend='nccl',
        init_method='env://',
        world_size=world_size,
        rank=rank,
    )
    torch.cuda.set_device(local_rank)
    return rank, world_size, local_rank


def cleanup():
    dist.destroy_process_group()


def build_model(num_classes=10):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, num_classes)
    return model


def get_dataloaders(rank, world_size, batch_size, num_workers=8):
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    transform_val = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    # Only rank 0 downloads; others wait at the barrier
    if rank == 0:
        datasets.CIFAR10('./data', train=True,  download=True)
        datasets.CIFAR10('./data', train=False, download=True)
    dist.barrier()

    train_set = datasets.CIFAR10('./data', train=True,  transform=transform_train)
    val_set   = datasets.CIFAR10('./data', train=False, transform=transform_val)

    train_sampler = DistributedSampler(train_set, num_replicas=world_size,
                                       rank=rank, shuffle=True)
    train_loader = DataLoader(train_set, batch_size=batch_size,
                              sampler=train_sampler,
                              num_workers=num_workers, pin_memory=True)
    # Validation runs on all ranks independently (no sampler needed)
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False,
                            num_workers=num_workers, pin_memory=True)
    return train_loader, val_loader, train_sampler


def train_epoch(model, loader, sampler, criterion, optimizer, device, epoch):
    model.train()
    sampler.set_epoch(epoch)   # ensures different data ordering per epoch
    total_loss, total_samples = 0.0, 0
    t0 = time.time()
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        total_samples += images.size(0)
    elapsed = time.time() - t0
    # throughput reported per-process; multiply by world_size for global throughput
    return total_loss / total_samples, total_samples / elapsed


def validate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            _, predicted = torch.max(model(images), 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    return 100.0 * correct / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs',     type=int,   default=20)
    parser.add_argument('--batch_size', type=int,   default=128)
    parser.add_argument('--lr',         type=float, default=0.1)
    parser.add_argument('--output_dir', type=str,   default='./results')
    args = parser.parse_args()

    rank, world_size, local_rank = setup()
    device = torch.device(f'cuda:{local_rank}')

    if rank == 0:
        print(f"Training on {world_size} GPUs")
        print(f"GPU: {torch.cuda.get_device_name(local_rank)}")
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    model = build_model().to(device)
    model = DDP(model, device_ids=[local_rank])

    criterion = nn.CrossEntropyLoss()
    # Linear scaling rule: multiply lr by world_size
    lr = args.lr * world_size
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    train_loader, val_loader, train_sampler = get_dataloaders(
        rank, world_size, args.batch_size)

    history = []
    for epoch in range(1, args.epochs + 1):
        loss, throughput = train_epoch(
            model, train_loader, train_sampler, criterion, optimizer, device, epoch)
        accuracy = validate(model, val_loader, device)
        scheduler.step()

        if rank == 0:
            global_throughput = throughput * world_size
            print(f"Epoch {epoch:3d} | loss {loss:.4f} | acc {accuracy:.2f}% "
                  f"| {global_throughput:.0f} samples/sec ({world_size} GPUs)")
            history.append({'epoch': epoch, 'loss': loss,
                            'accuracy': accuracy, 'throughput': global_throughput})

    # Only rank 0 saves the model
    if rank == 0:
        torch.save(model.module.state_dict(), f'{args.output_dir}/model.pt')
        with open(f'{args.output_dir}/results.json', 'w') as f:
            json.dump(history, f, indent=2)

    cleanup()

if __name__ == '__main__':
    main()
```

### Expected throughput (ResNet-18 on CIFAR-10)

| GPUs | Node(s) | Approx. throughput | Notes |
|---|---|---|---|
| 1 | 1 | ~4,000 samples/sec | Baseline |
| 2 | 1 | ~7,500 samples/sec | ~1.9× — NVLink keeps overhead low |
| 4 | 1 | ~14,000 samples/sec | ~3.5× — slight communication overhead |
| 2 | 2 | ~7,000 samples/sec | Slightly less than 2× single-node — inter-node bandwidth (a30) |
| 8 | 4 | ~25,000 samples/sec | ~6× — InfiniBand overhead grows with node count (requires h200, coming soon) |

Numbers will vary by GPU model and network interconnect.

---

## Multi-Node Distributed Training

Scaling across multiple nodes uses the same `train_ddp.py` script. The SLURM script changes to request multiple nodes and set the right NCCL variables for inter-node communication.

!!! note "Which partition for multi-node GPU jobs?"
    Today, multi-node GPU training runs on the **`a30`** partition (up to 2 nodes, 2 GPUs each = 4 GPUs). The `h100` partition is limited to a single node per job. The larger **`h200`** partition (coming soon — see [GPU Computing on Juno](index.md)) will support bigger multi-node runs. The example below uses `a30` so it runs on current hardware.

### SLURM script

```bash
#!/bin/bash
#SBATCH -J train_ddp_multinode
#SBATCH -o logs/ddp_multinode_%j.out
#SBATCH -e logs/ddp_multinode_%j.err
#SBATCH -p a30                   # multi-node GPU partition (h200 coming soon for larger runs)
#SBATCH -N 2                     # number of nodes
#SBATCH --ntasks-per-node=2      # 2 GPUs per a30 node = 4 GPUs total
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=256GB
#SBATCH -t 8:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=29500
# Allow NCCL to use InfiniBand for inter-node communication
export NCCL_IB_DISABLE=0
export NCCL_DEBUG=WARN       # set to INFO for verbose NCCL diagnostics

echo "Master node: $MASTER_ADDR"
echo "Total tasks (GPUs): $SLURM_NTASKS"
echo "Nodes: $SLURM_JOB_NODELIST"

srun python train_ddp.py \
    --epochs 20 \
    --batch_size 128 \
    --lr 0.1 \
    --output_dir ./results
```

### What changes for multi-node

The `train_ddp.py` script above already handles multi-node through SLURM's environment variables:

| Variable | What it sets | Example (2 nodes × 2 GPUs) |
|---|---|---|
| `SLURM_PROCID` | Global rank of this process | 0–3 |
| `SLURM_NTASKS` | Total number of processes (world size) | 4 |
| `SLURM_LOCALID` | Local GPU index on this node | 0 or 1 |
| `MASTER_ADDR` | Hostname of rank-0 node (set in script) | `g-01-01` |
| `MASTER_PORT` | Port for the rendezvous (set in script) | `29500` |

No code changes are needed to go from single-node to multi-node — only the SLURM directives change.

### Checking inter-node connectivity

```bash
# While job is running, from the login node:
scontrol show job $JOBID | grep NodeList

# From within the job (add to your script):
srun hostname | sort    # prints all allocated hostnames
```

### NCCL environment variables

| Variable | When to use |
|---|---|
| `NCCL_P2P_DISABLE=1` | GPUs on the same node are NOT connected by NVLink (prevents failed P2P attempts). On Juno, only `g-04-02` (4× H100) has NVLink — set this on other multi-GPU nodes, but **not** on `g-04-02` |
| `NCCL_IB_DISABLE=1` | Disable InfiniBand (use only for single-node jobs or debugging) |
| `NCCL_IB_DISABLE=0` | Enable InfiniBand for multi-node communication (default on Juno) |
| `NCCL_DEBUG=INFO` | Print detailed NCCL transport selection — useful when debugging hang/timeout |
| `NCCL_SOCKET_IFNAME=ib0` | Force NCCL to use a specific network interface |

---

## Monitoring a Running Training Job

### Check GPU utilization in real time

```bash
# SSH to a compute node allocated to your job
ssh $(squeue -j $JOBID -h -o "%N" | head -n1)

# Watch GPU utilization every 2 seconds
watch -n 2 nvidia-smi
```

Target: GPU utilization should be consistently **> 80%**. If it's lower, the bottleneck is likely data loading (increase `num_workers`) or the batch size is too small.

### Check job efficiency after completion

```bash
module load jobstats
jobstats $JOBID
```

See [Monitoring Jobs and Cluster State](../running-programs/advanced-slurm.md) for details on interpreting `jobstats` output.

### Watch training logs live

```bash
tail -f logs/ddp_multinode_${JOBID}.out
```

---

## Job Submission Checklist

Before submitting a long multi-GPU run:

1. **Test on 1 GPU first** — confirm the script runs without errors for 1–2 epochs
2. **Check memory** — use `nvidia-smi` to confirm your batch size fits in VRAM before scaling up
3. **Verify DDP is actually being used** — print `dist.get_world_size()` at startup to confirm all processes connected
4. **Set appropriate time limits** — run a short benchmark to estimate time per epoch, then request 2× that for the full run
5. **Use `--mail-type=END,FAIL`** — get notified when the job finishes or crashes

---

## Related Pages

- [GPU Computing on Juno](index.md) — GPU partitions, environment setup
- [GPU Performance & Monitoring](gpu-performance.md) — mixed precision, profiling, memory tips
- [Common Scientific Programs](../running-programs/common-programs.md) — job scripts for other frameworks
- [Containers](../advanced/containers.md) — running vLLM, AlphaFold, Stable Diffusion in containers
