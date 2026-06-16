# PyTorch Training Tutorial

This is a complete, worked PyTorch example that runs **as-is** on Juno's GPUs. It starts on a single GPU, then scales to multiple GPUs on one node, then to multiple nodes — all with the *same* training script. Every script on this page has been run on Juno's H200 nodes and works without modification.

Along the way it explains the parts that usually trip people up on a real cluster: how PyTorch processes find each other (the rendezvous), and the **NCCL environment variables** that control GPU-to-GPU communication — what each one does and why it matters on Juno's specific hardware.

---

## Prerequisites

- A Conda environment with a CUDA 12.x PyTorch build (`torch >= 2.3`). See [GPU Computing on Juno](index.md) for setup instructions.
- Familiarity with SLURM job submission. See [SLURM Job Scheduler](../running-programs/slurm.md).

!!! note "Which partition"
    The job scripts below target the **H200 nodes** (141 GB HBM3e, 2 GPUs/node, no NVLink, 400 Gb InfiniBand). The NCCL settings are tuned for that node's topology. If you adapt this to the `h100` or `a30` partitions, re-check the interconnect settings — those nodes have a different layout (see [Understanding the NCCL settings](#understanding-the-nccl-settings)).

---

## About this example

The script trains a **GPT-style transformer** (a stack of attention + MLP blocks, nanoGPT-style). Two deliberate choices make it a clean teaching example that runs smoothly:

- **Synthetic data.** Each batch is random tokens generated directly on the GPU. There's no dataset to download, no data loader to misconfigure, and the CPU/disk can never become the bottleneck — so the example *just runs*, and what you measure is the GPU and the interconnect. Swap in real data once the mechanics are working.
- **A compute-heavy model.** Each training step does milliseconds of dense matrix-multiply, so the GPUs are genuinely busy. This matters when you scale up: distributed training synchronizes gradients every step, and that synchronization only "pays off" when each step does enough real compute to hide it.

!!! tip "Why not a small model like CIFAR-10?"
    A tiny model is a poor first distributed example: its per-step compute is microseconds, so adding GPUs makes it *slower* — you end up measuring synchronization overhead, not training. Starting with a compute-heavy model means scaling behaves the way you'd expect (more GPUs → more throughput), which makes the tutorial's lessons transferable.

The script reports throughput (tokens/sec) and GPU utilization so you can confirm each step is working before moving to the next.

---

## The training script — `train.py`

This single file runs unchanged on 1 GPU, on one multi-GPU node, and across many nodes. It reads its identity (`RANK` / `WORLD_SIZE` / `LOCAL_RANK`) from the environment, which the launcher (`torchrun` or SLURM's `srun`) sets for each process. With `WORLD_SIZE=1` it skips all distributed setup entirely, so the single-GPU path has zero distributed machinery to go wrong.

```python
"""
PyTorch distributed training example: a GPT-style transformer.

Runs identically on 1 GPU, multi-GPU (one node), or multi-node, launched via
torchrun or SLURM/srun. Reports tokens/sec, per-GPU and aggregate throughput,
model-FLOPs-utilization (MFU), and peak memory so you can confirm the GPUs are
being used well.

Parallelism:
  --parallel ddp   gradient all-reduce, full model replicated per GPU (default)
  --parallel fsdp  fully-sharded data parallel; shards params/grads/optimizer
                   state across ranks. Use for models too big to fit on one GPU.

Data is synthetic so the dataloader never bottlenecks the GPUs and the example
runs with no external dependencies. Swap in real data once the mechanics work.
"""

import argparse
import contextlib
import math
import os
import time
from dataclasses import dataclass

import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint
from torch.nn.parallel import DistributedDataParallel as DDP


# --------------------------------------------------------------------------- #
# Model: a standard pre-norm GPT (nanoGPT-style), big enough to be compute-bound
# --------------------------------------------------------------------------- #
@dataclass
class GPTConfig:
    vocab_size: int = 50304   # padded to a multiple of 64 for tensor-core efficiency
    block_size: int = 2048    # sequence length
    n_layer: int = 24
    n_head: int = 16
    n_embd: int = 2048
    dropout: float = 0.0      # 0 for a clean example: deterministic compute, no RNG cost


class CausalSelfAttention(nn.Module):
    """Multi-head causal attention via fused scaled_dot_product_attention.

    Using is_causal=True (instead of an explicit additive -inf mask) lets
    PyTorch dispatch to the FlashAttention kernel on H100/H200, which avoids
    materializing the T x T attention matrix and is the single biggest speed win
    over nn.MultiheadAttention + a float mask.
    """
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0
        self.n_head = cfg.n_head
        self.n_embd = cfg.n_embd
        self.dropout = cfg.dropout
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd)   # fused q,k,v projection
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(self.n_embd, dim=2)
        # (B, T, C) -> (B, n_head, T, head_dim)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        y = F.scaled_dot_product_attention(
            q, k, v, is_causal=True,
            dropout_p=self.dropout if self.training else 0.0,
        )
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class Block(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.n_embd)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.n_embd)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.n_embd, 4 * cfg.n_embd),
            nn.GELU(),
            nn.Linear(4 * cfg.n_embd, cfg.n_embd),
            nn.Dropout(cfg.dropout),
        )

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class GPT(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.cfg = cfg
        self.grad_checkpoint = False   # set by main(); recompute activations to save memory
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        self.tok_emb.weight = self.head.weight  # weight tying

    def forward(self, idx, targets):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok_emb(idx) + self.pos_emb(pos)[None, :, :]
        for blk in self.blocks:
            if self.grad_checkpoint and self.training:
                # non-reentrant checkpoint is the FSDP-compatible variant: it
                # frees per-layer activations and recomputes them in backward,
                # trading ~30% extra compute for a large activation-memory cut.
                x = torch.utils.checkpoint.checkpoint(blk, x, use_reentrant=False)
            else:
                x = blk(x)
        logits = self.head(self.ln_f(x))
        loss = F.cross_entropy(
            logits.view(-1, logits.size(-1)), targets.view(-1)
        )
        return loss

    def num_params(self):
        # exclude the tied head (shares storage with tok_emb)
        return sum(p.numel() for p in self.parameters()) - self.head.weight.numel()


def flops_per_token(model: GPT) -> float:
    """Forward+backward FLOPs per token (PaLM / nanoGPT estimate)."""
    cfg = model.cfg
    N = model.num_params()
    head_dim = cfg.n_embd // cfg.n_head
    # 6N (fwd+bwd dense) + attention term (12 * layers * heads * head_dim * seqlen)
    return 6 * N + 12 * cfg.n_layer * cfg.n_head * head_dim * cfg.block_size


# --------------------------------------------------------------------------- #
# Distributed setup
# --------------------------------------------------------------------------- #
def setup_dist():
    """Reads rank/world from env (set by torchrun or srun) and inits NCCL.

    On a single GPU (WORLD_SIZE=1) this skips the process group entirely, so the
    baseline run needs no rendezvous and no NCCL — it just trains.
    """
    rank = int(os.environ.get("RANK", 0))
    world = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    if world > 1:
        dist.init_process_group(backend="nccl")
    torch.cuda.set_device(local_rank)
    return rank, world, local_rank


def is_main(rank):
    return rank == 0


def log(rank, *a):
    if is_main(rank):
        print(*a, flush=True)


# --------------------------------------------------------------------------- #
# Training loop
# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--parallel", choices=["ddp", "fsdp"], default="ddp")
    p.add_argument("--micro-batch", type=int, default=12, help="per-GPU batch")
    p.add_argument("--block-size", type=int, default=2048)
    p.add_argument("--n-layer", type=int, default=24)
    p.add_argument("--n-head", type=int, default=16)
    p.add_argument("--n-embd", type=int, default=2048)
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--warmup", type=int, default=10, help="steps excluded from timing")
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--compile", action="store_true", help="torch.compile the model")
    p.add_argument("--grad-checkpoint", action="store_true")
    p.add_argument("--peak-tflops", type=float, default=989.0,
                   help="per-GPU peak for MFU; H200 SXM BF16 dense ~989")
    args = p.parse_args()

    rank, world, local_rank = setup_dist()
    device = f"cuda:{local_rank}"
    torch.manual_seed(1234 + rank)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    cfg = GPTConfig(block_size=args.block_size, n_layer=args.n_layer,
                    n_head=args.n_head, n_embd=args.n_embd)
    model = GPT(cfg).to(device)

    # capture model stats from the unwrapped GPT, before DDP/FSDP hide them
    n_params = model.num_params()
    fpt = flops_per_token(model)

    # trades ~30% compute for a large activation-memory saving; applied inside
    # GPT.forward so it composes correctly with DDP and FSDP wrapping below.
    model.grad_checkpoint = args.grad_checkpoint

    # wrap for the chosen parallelism strategy
    if world > 1 and args.parallel == "ddp":
        model = DDP(model, device_ids=[local_rank])
    elif world > 1 and args.parallel == "fsdp":
        from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
        from torch.distributed.fsdp import MixedPrecision
        from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
        import functools
        mp = MixedPrecision(param_dtype=torch.bfloat16,
                            reduce_dtype=torch.bfloat16,
                            buffer_dtype=torch.bfloat16)
        wrap = functools.partial(transformer_auto_wrap_policy,
                                 transformer_layer_cls={Block})
        model = FSDP(model, auto_wrap_policy=wrap, mixed_precision=mp,
                     device_id=local_rank)

    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, fused=True)

    if args.compile:
        model = torch.compile(model)

    autocast = (
        torch.autocast("cuda", dtype=torch.bfloat16) if args.dtype == "bf16"
        else torch.autocast("cuda", dtype=torch.float16) if args.dtype == "fp16"
        else contextlib.nullcontext()
    )
    scaler = torch.amp.GradScaler("cuda", enabled=args.dtype == "fp16")

    # synthetic batch: random tokens, regenerated cheaply on-GPU each step
    def get_batch():
        x = torch.randint(0, cfg.vocab_size, (args.micro_batch, cfg.block_size),
                          device=device)
        y = torch.randint(0, cfg.vocab_size, (args.micro_batch, cfg.block_size),
                          device=device)
        return x, y

    if is_main(rank):
        print(f"world_size={world}  parallel={args.parallel}  dtype={args.dtype}")
        print(f"params={n_params/1e6:.1f}M  block={cfg.block_size}  "
              f"micro_batch={args.micro_batch}  global_tokens/step="
              f"{args.micro_batch*cfg.block_size*world}")

    step_times = []
    for step in range(args.steps):
        if step == args.warmup:
            torch.cuda.synchronize()
            dist.barrier() if world > 1 else None
            t0 = time.perf_counter()

        x, y = get_batch()
        with autocast:
            loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        if scaler.is_enabled():
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
        else:
            loss.backward()
            opt.step()

    torch.cuda.synchronize()
    if world > 1:
        dist.barrier()
    elapsed = time.perf_counter() - t0
    timed_steps = args.steps - args.warmup

    # aggregate throughput
    tokens_per_step_global = args.micro_batch * cfg.block_size * world
    total_tokens = tokens_per_step_global * timed_steps
    tok_per_sec = total_tokens / elapsed
    per_gpu_tok_per_sec = tok_per_sec / world

    # MFU: achieved FLOPs/s vs peak. fpt is per-token fwd+bwd FLOPs.
    achieved_flops = fpt * tok_per_sec          # whole job
    peak_flops = args.peak_tflops * 1e12 * world
    mfu = achieved_flops / peak_flops

    peak_mem = torch.cuda.max_memory_allocated(device) / 1e9

    if is_main(rank):
        print("-" * 60)
        print(f"timed_steps        : {timed_steps}")
        print(f"step_time (avg)    : {elapsed/timed_steps*1e3:.1f} ms")
        print(f"throughput (total) : {tok_per_sec/1e3:.1f}k tokens/s")
        print(f"throughput (/GPU)  : {per_gpu_tok_per_sec/1e3:.1f}k tokens/s")
        print(f"MFU                : {mfu*100:.1f}%")
        print(f"peak mem (/GPU)    : {peak_mem:.1f} GB")
        # one machine-readable line, handy if you collect many runs into a table
        print(f"RESULT world={world} parallel={args.parallel} "
              f"tok_s={tok_per_sec:.0f} tok_s_per_gpu={per_gpu_tok_per_sec:.0f} "
              f"mfu={mfu:.4f} step_ms={elapsed/timed_steps*1e3:.1f} "
              f"peak_gb={peak_mem:.2f}")

    if world > 1:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
```

!!! note "Why BF16 + FlashAttention"
    Attention uses the fused `scaled_dot_product_attention` kernel (FlashAttention on H100/H200), which never materializes the T×T attention matrix — the single biggest speed lever. BF16 has the same dynamic range as FP32, so it rarely needs gradient scaling. See [GPU Performance & Monitoring](gpu-performance.md) for more on mixed precision.

---

## Step 1 — Single GPU

Always start here. It confirms your environment, the model, and the GPU all work before any distributed machinery is involved. With `WORLD_SIZE=1` the script doesn't touch NCCL at all.

### `submit_singlegpu.sbatch`

```bash
#!/bin/bash
#SBATCH --job-name=train-1gpu
#SBATCH --nodes=1                  # single node
#SBATCH --ntasks-per-node=1        # 1 process = 1 GPU
#SBATCH --gpus-per-node=1          # 1 GPU
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --partition=h200
#SBATCH --output=logs/train_1gpu_%j.log
#SBATCH --error=logs/train_1gpu_%j.err

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

mkdir -p logs

# WORLD_SIZE=1, so train.py skips NCCL/process-group init entirely — no
# MASTER_ADDR or interconnect tuning needed for a single GPU.
srun --kill-on-bad-exit=1 bash -c '
  export RANK=0
  export WORLD_SIZE=1
  export LOCAL_RANK=0
  python train.py \
      --parallel ddp \
      --micro-batch 12 \
      --n-layer 24 --n-embd 2048 --n-head 16 \
      --block-size 2048 \
      --dtype bf16 \
      --steps 60 --warmup 10
'
```

Submit it, then check the log for the `throughput` and `MFU` lines. A healthy single-GPU run on an H200 lands around 40–55% MFU. If it runs, you're ready to scale.

---

## Step 2 — Multiple GPUs on one node (DDP)

PyTorch's `DistributedDataParallel` (DDP) is the standard way to use more than one GPU. Each GPU runs a full copy of the model and processes a different slice of the batch; after each backward pass, the gradients are averaged across all GPUs with an **all-reduce** so every copy stays in sync. That all-reduce is the GPU-to-GPU communication that NCCL handles — and the reason the settings in the next section matter.

DDP needs **one process per GPU**, which is why `--ntasks-per-node` equals `--gpus-per-node`. SLURM launches the processes; each one reads its rank from `SLURM_PROCID` and we map that to the `RANK` / `WORLD_SIZE` / `LOCAL_RANK` names PyTorch expects.

### `submit_singlenode.sbatch`

```bash
#!/bin/bash
#SBATCH --job-name=train-1node
#SBATCH --nodes=1                  # single node
#SBATCH --ntasks-per-node=2        # 2 processes = 2 GPUs
#SBATCH --gpus-per-node=2          # 2 GPUs
#SBATCH --cpus-per-task=8          # match the 8 NUMA-local cores per GPU (24-31 / 32-39)
#SBATCH --time=00:30:00
#SBATCH --partition=h200
#SBATCH --output=logs/train_1node_%j.log
#SBATCH --error=logs/train_1node_%j.err

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

mkdir -p logs

# ---- rendezvous: where the processes find each other ----
# Rank 0's hostname is the meeting point; every process connects to MASTER_ADDR
# on MASTER_PORT to form the process group. Without this, the ranks can't init.
MASTER_ADDR=$(scontrol show hostnames $SLURM_NODELIST | head -n 1)
export MASTER_ADDR
export MASTER_PORT=29500

# ---- NCCL: tell it how these two GPUs talk to each other ----
# (See "Understanding the NCCL settings" below for what each line does.)
export NCCL_P2P_LEVEL=SYS    # allow GPU-to-GPU transfers across the CPU sockets
export NCCL_DEBUG=INFO       # log the transport NCCL actually chose

# Map SLURM's per-task env to the RANK/WORLD_SIZE/LOCAL_RANK that train.py reads.
# --cpu-bind=cores pins each rank to its GPU's NUMA-local CPU cores.
srun --kill-on-bad-exit=1 --cpu-bind=cores bash -c '
  export RANK=$SLURM_PROCID
  export WORLD_SIZE=$SLURM_NTASKS
  export LOCAL_RANK=$SLURM_LOCALID
  python train.py \
      --parallel ddp \
      --micro-batch 12 \
      --n-layer 24 --n-embd 2048 --n-head 16 \
      --block-size 2048 \
      --dtype bf16 \
      --steps 60 --warmup 10
'
```

The per-GPU batch (`--micro-batch`) stays the same, so two GPUs process twice the data per step. Throughput should rise — though, on these no-NVLink nodes, not by a perfect 2× (the next section explains why).

!!! tip "Sweep 1→2→4→8 GPUs interactively"
    For a quick scaling check on an allocated node, `run_single_node.sh` runs the same workload at each GPU count back-to-back using `torchrun` (which launches all the processes from a single shell, so you don't need a separate `srun` wrapper):

    ```bash
    #!/usr/bin/env bash
    # Usage:  ./run_single_node.sh [ddp|fsdp]
    set -euo pipefail

    export NCCL_P2P_LEVEL=SYS
    export NCCL_DEBUG=INFO

    PARALLEL="${1:-ddp}"
    GPUS_ON_NODE="$(nvidia-smi -L | wc -l)"

    ARGS="--parallel ${PARALLEL} --micro-batch 12 --n-layer 24 --n-embd 2048 \
          --n-head 16 --block-size 2048 --dtype bf16 --steps 60 --warmup 10"

    for N in 1 2 4 8; do
      if [ "$N" -gt "$GPUS_ON_NODE" ]; then continue; fi
      echo "=================  $N GPU(s)  ================="
      torchrun --standalone --nproc_per_node="$N" train.py $ARGS
      echo
    done
    ```

---

## Step 3 — Multiple nodes (over InfiniBand)

Going from one node to several uses the *same* `train.py` and the *same* model arguments. Only two things change: the SLURM directives request more nodes, and a few extra NCCL variables tell NCCL to communicate **between** nodes over InfiniBand instead of just within a node.

### `submit_multinode.sbatch`

```bash
#!/bin/bash
#SBATCH --job-name=train-multinode
#SBATCH --nodes=2                  # <-- set node count here (or override on submit)
#SBATCH --ntasks-per-node=2        # one process per GPU; this node type has 2 GPUs
#SBATCH --gpus-per-node=2          # 2 GPUs per node
#SBATCH --cpus-per-task=8          # match the 8 NUMA-local cores per GPU (24-31 / 32-39)
#SBATCH --exclusive                # whole, unshared nodes for stable timing
#SBATCH --time=00:30:00
#SBATCH --partition=h200
#SBATCH --output=logs/train_multi_%j.log
#SBATCH --error=logs/train_multi_%j.err
#
# Submit with:        sbatch submit_multinode.sbatch
# Scale out:          sbatch --nodes=4 submit_multinode.sbatch     # 4 nodes = 8 GPUs
# Try FSDP instead:   PARALLEL=fsdp sbatch submit_multinode.sbatch

module purge
module load gnu14
module load miniconda
module load cuda/12.6

conda activate gpu-env

mkdir -p logs

# ---- rendezvous: node 0 is the meeting point ----
MASTER_ADDR=$(scontrol show hostnames $SLURM_NODELIST | head -n 1)
export MASTER_ADDR
export MASTER_PORT=29500

# ---- NCCL tuning for PCIe + InfiniBand (NO NVLink) ----
# Each line is explained in "Understanding the NCCL settings" below.
export NCCL_IB_DISABLE=0                  # use InfiniBand for inter-node traffic
export NCCL_NET_GDR_LEVEL=${NCCL_NET_GDR_LEVEL:-SYS}  # allow GPUDirect RDMA across the socket
export NCCL_IB_HCA=mlx5_0                 # the InfiniBand NIC on these nodes
export NCCL_IB_PCI_RELAXED_ORDERING=1     # PCIe relaxed ordering — often a big GDR win
export NCCL_P2P_LEVEL=SYS                 # allow intra-node GPU-to-GPU across the socket
export NCCL_SOCKET_IFNAME=^lo,docker0     # keep loopback/docker out of the bootstrap handshake
export NCCL_DEBUG=INFO                    # confirm "NET/IB" and "[GPUDirect RDMA]" in the log
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1  # surface a hung/crashed rank instead of deadlocking

# Reduce allocator fragmentation; helps avoid OOM near the memory ceiling.
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

PARALLEL="${PARALLEL:-ddp}"

ARGS="--parallel ${PARALLEL} --micro-batch 12 --n-layer 24 --n-embd 2048 \
      --n-head 16 --block-size 2048 --dtype bf16 --steps 60 --warmup 10"

# Map SLURM's per-task env to the RANK/WORLD_SIZE/LOCAL_RANK that train.py reads.
srun --kill-on-bad-exit=1 --cpu-bind=cores bash -c '
  export RANK=$SLURM_PROCID
  export WORLD_SIZE=$SLURM_NTASKS
  export LOCAL_RANK=$SLURM_LOCALID
  python train.py '"$ARGS"'
'
```

No code changes are needed to go from one node to many — only the SLURM directives and the inter-node NCCL variables:

```bash
sbatch submit_multinode.sbatch                  # 2 nodes = 4 GPUs
sbatch --nodes=4 submit_multinode.sbatch        # 4 nodes = 8 GPUs
PARALLEL=fsdp sbatch submit_multinode.sbatch    # shard a too-big model with FSDP
```

---

## Understanding the NCCL settings

This section is the heart of getting multi-GPU PyTorch to run *well* on Juno. It's worth reading even if the scripts above already work for you.

**What NCCL is.** NCCL (the NVIDIA Collective Communications Library, pronounced "nickel") is what actually moves data between GPUs when DDP averages gradients or FSDP gathers shards. PyTorch calls into it; you rarely call it directly. NCCL tries to auto-detect the fastest path between any two GPUs — NVLink if present, otherwise PCIe, otherwise the network. **The reason we set anything at all is that auto-detection makes conservative choices on unusual hardware, and Juno's H200 nodes are unusual in two ways that matter.**

### The hardware NCCL has to work with

`nvidia-smi topo -m` on an H200 node reports two GPUs on **different NUMA nodes** (i.e. attached to different CPU sockets) and a **single InfiniBand NIC**, with every path between them marked `SYS`:

```
        GPU0   GPU1   NIC0   CPU Affinity   NUMA
GPU0     X     SYS    SYS    24-31          3
GPU1    SYS     X     SYS    32-39          4
NIC0    SYS    SYS     X
```

`SYS` means the connection traverses PCIe **and** the link between the two CPU sockets (Intel calls it UPI). Two consequences follow, and they drive every setting below:

1. **There is no NVLink.** GPU-to-GPU traffic on one node rides PCIe and crosses between sockets — much slower than NVLink. So intra-node scaling won't be a perfect 2×, and that's the hardware, not a bug.
2. **The NIC is "far" from both GPUs.** Because the single InfiniBand card is cross-socket from each GPU, the fast network path (GPUDirect RDMA) is one that NCCL's defaults would *silently disable* unless we tell it the card is reachable at the `SYS` level.

### The variables, and why each matters

| Variable | Value | What it does | Why it matters on Juno |
|---|---|---|---|
| `MASTER_ADDR` / `MASTER_PORT` | rank-0 host, `29500` | The rendezvous point: every process connects here to form the group. | Not NCCL itself, but DDP can't start without it. We set it to the first node in the allocation. |
| `NCCL_IB_DISABLE` | `0` | Allow NCCL to use InfiniBand for the network. | Inter-node gradient sync must go over the 400 Gb IB fabric, not slow TCP. `0` = enabled. |
| `NCCL_IB_HCA` | `mlx5_0` | Names the specific InfiniBand card to use. | These nodes have one IB NIC; naming it avoids NCCL probing/guessing the wrong device. |
| `NCCL_NET_GDR_LEVEL` | `SYS` | The maximum topology distance at which **GPUDirect RDMA** (NIC reads/writes GPU memory directly, skipping the CPU) is allowed. | The NIC is `SYS` from both GPUs. The default (`PHB`/`PXB`) is "closer" than `SYS`, so it would *silently turn GDR off* here. `SYS` keeps the fast path available. |
| `NCCL_P2P_LEVEL` | `SYS` | The maximum distance at which direct GPU-to-GPU (peer) transfers are allowed. | Lets the two cross-socket GPUs attempt direct transfers. If the platform can't do cross-socket peer DMA, NCCL falls back to shared host memory — which is the expected behavior here, not an error. |
| `NCCL_IB_PCI_RELAXED_ORDERING` | `1` | Enables PCIe relaxed-ordering for IB transfers. | Frequently a large throughput win for GPUDirect RDMA on this kind of topology; safe to enable. |
| `NCCL_SOCKET_IFNAME` | `^lo,docker0` | Which host network interfaces NCCL may use for its initial bootstrap handshake (`^` = exclude). | Excludes loopback and the docker bridge so the rendezvous doesn't bind to a useless interface and hang at startup. |
| `NCCL_DEBUG` | `INFO` | Verbosity of NCCL's own logging. | Prints which transport NCCL chose — the only reliable way to confirm IB and GDR are actually being used (see below). |
| `TORCH_NCCL_ASYNC_ERROR_HANDLING` | `1` | If one rank crashes or a collective times out, tear the job down instead of hanging forever. | Turns a silent multi-hour deadlock into a prompt, debuggable failure. |
| `PYTORCH_CUDA_ALLOC_CONF` | `expandable_segments:True` | PyTorch allocator setting (not NCCL). | Reduces memory fragmentation, which helps avoid out-of-memory errors when you push the model size toward the 141 GB ceiling. |

!!! warning "The two settings most likely to silently hurt you"
    `NCCL_NET_GDR_LEVEL` and `NCCL_P2P_LEVEL` are the ones to understand. Because Juno's NIC and GPUs are all `SYS`-distance apart, leaving these at their defaults doesn't produce an error — it quietly disables the fast paths, and your multi-node job just runs slower than it should. Setting both to `SYS` is what *permits* the fast path; whether it's actually used you confirm from the log.

### Is cross-socket GDR actually faster? A/B test it

There's one case where the "fast" path isn't faster: DMA-ing GPU memory across the socket link to a far NIC can sometimes be *slower* than staging through host RAM. The setting that's optimal here is empirical, so test both:

```bash
sbatch submit_multinode.sbatch                         # GDR on  (SYS, the default above)
NCCL_NET_GDR_LEVEL=LOC sbatch submit_multinode.sbatch  # GDR off (host staging)
```

Keep whichever gives higher throughput. (The override works because an environment variable set at submit time propagates through `srun` to every rank.)

### Confirm it worked — read the `NCCL_DEBUG=INFO` log

On the first multi-node run, check the job log for:

- **InfiniBand, not TCP:** look for `NET/IB` / `via IB`. If you instead see `NET/Socket`, NCCL fell back to slow TCP — fix `NCCL_IB_HCA` (get the name from `ibstat`) and `NCCL_SOCKET_IFNAME`.
- **GDR active:** look for `[GPUDirect RDMA]` or `GDRDMA` on the IB lines. If it's missing even with `SYS`, the `nvidia-peermem` kernel module probably isn't loaded — GDR is impossible without it.
- **Intra-node path:** `P2P/direct` means direct peer DMA; `SHM` means it bounced through host memory. On these cross-socket nodes, `SHM` is the *expected* result, not a misconfiguration.

---

## Reading the output

Each run prints a short summary plus one machine-readable `RESULT` line:

| Line | What it tells you |
|---|---|
| `throughput (total)` | Tokens/sec across all GPUs — the headline number. |
| `throughput (/GPU)` | Per-GPU tokens/sec. Should stay roughly flat as you add GPUs; a drop means communication is eating the gains. |
| `MFU` | Fraction of the GPU's peak FLOPs you're achieving. ~40–55% is healthy for a dense transformer; much lower means the GPU is being starved. |
| `step_time (avg)` | Wall-clock per training step. How much it grows when you add GPUs is the *exposed* communication cost. |
| `peak mem (/GPU)` | How close you are to the 141 GB ceiling — your headroom for a bigger model or batch. |

??? note "Optional: collect many runs into one table with `aggregate_results.py`"
    If you run the example at several GPU counts, this helper scrapes the `RESULT` lines from your logs into a scaling table (and optionally a CSV or plot):

    ```bash
    python aggregate_results.py                      # scan logs/*.log + *.out
    python aggregate_results.py --csv out.csv        # also write a CSV
    python aggregate_results.py --plot scaling.png   # throughput plot (needs matplotlib)
    ```

    ```python
    """
    Scrape RESULT lines from training logs into a CSV + scaling table.

    train.py emits one machine-readable line per run, e.g.:
        RESULT world=2 parallel=ddp tok_s=812345 tok_s_per_gpu=406172 mfu=0.4500 \
               step_ms=20.1 peak_gb=40.50

    Scaling efficiency is computed per parallelism mode, relative to the smallest
    world size found for that mode (your baseline — ideally world=1):
        efficiency(N) = tok_s_per_gpu(N) / tok_s_per_gpu(baseline)
        speedup(N)    = tok_s(N)        / tok_s(baseline)
    """

    import argparse
    import csv
    import glob
    import re
    import sys

    FIELDS = ["world", "parallel", "tok_s", "tok_s_per_gpu", "mfu", "step_ms", "peak_gb"]
    TYPES = {"world": int, "parallel": str, "tok_s": float, "tok_s_per_gpu": float,
             "mfu": float, "step_ms": float, "peak_gb": float}

    LINE_RE = re.compile(r"\bRESULT\b(?P<body>.*)")
    KV_RE = re.compile(r"(\w+)=([^\s]+)")


    def parse_files(patterns):
        rows = []
        seen_files = []
        for pat in patterns:
            for path in sorted(glob.glob(pat)):
                seen_files.append(path)
                with open(path, "r", errors="replace") as fh:
                    for line in fh:
                        m = LINE_RE.search(line)
                        if not m:
                            continue
                        kv = dict(KV_RE.findall(m.group("body")))
                        if "world" not in kv:           # not one of our RESULT lines
                            continue
                        try:
                            row = {k: TYPES[k](kv[k]) for k in FIELDS if k in kv}
                        except (KeyError, ValueError):
                            continue
                        row["source"] = path
                        rows.append(row)
        return rows, seen_files


    def add_scaling(rows):
        """Annotate each row with speedup + efficiency vs its mode's baseline."""
        baselines = {}  # parallel -> baseline row (smallest world)
        for r in rows:
            mode = r.get("parallel", "?")
            if mode not in baselines or r["world"] < baselines[mode]["world"]:
                baselines[mode] = r
        for r in rows:
            base = baselines[r.get("parallel", "?")]
            r["speedup"] = r["tok_s"] / base["tok_s"] if base["tok_s"] else float("nan")
            r["efficiency"] = (r["tok_s_per_gpu"] / base["tok_s_per_gpu"]
                               if base["tok_s_per_gpu"] else float("nan"))
            r["_base_world"] = base["world"]
        return rows


    def print_table(rows):
        rows = sorted(rows, key=lambda r: (r.get("parallel", ""), r["world"]))
        hdr = ["parallel", "GPUs", "tok/s", "tok/s/GPU", "MFU%", "step_ms",
               "speedup", "scaling_eff", "peak_GB"]
        widths = [9, 5, 12, 12, 6, 8, 8, 12, 8]

        def fmt_row(cells):
            return "  ".join(str(c).rjust(w) for c, w in zip(cells, widths))

        print(fmt_row(hdr))
        print(fmt_row(["-" * w for w in widths]))
        for r in rows:
            ideal = r["world"] / r["_base_world"]
            eff = r["efficiency"]
            flag = ""
            if r["world"] > r["_base_world"] and eff < 0.8:
                flag = "  <- comm-bound?"
            print(fmt_row([
                r.get("parallel", "?"),
                r["world"],
                f"{r['tok_s']/1e3:.1f}k",
                f"{r['tok_s_per_gpu']/1e3:.1f}k",
                f"{r['mfu']*100:.1f}",
                f"{r['step_ms']:.1f}",
                f"{r['speedup']:.2f}x",
                f"{eff*100:.0f}% /{ideal:.0f}x",
                f"{r['peak_gb']:.1f}",
            ]) + flag)


    def write_csv(rows, path):
        cols = FIELDS + ["speedup", "efficiency", "source"]
        rows = sorted(rows, key=lambda r: (r.get("parallel", ""), r["world"]))
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {path}")


    def make_plot(rows, path):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available; skipping --plot", file=sys.stderr)
            return
        fig, ax = plt.subplots(figsize=(7, 5))
        modes = sorted({r.get("parallel", "?") for r in rows})
        for mode in modes:
            pts = sorted((r for r in rows if r.get("parallel") == mode),
                         key=lambda r: r["world"])
            xs = [r["world"] for r in pts]
            ys = [r["tok_s"] / 1e3 for r in pts]
            ax.plot(xs, ys, "o-", label=f"{mode} (measured)")
            if pts:
                base = pts[0]
                ideal = [base["tok_s"] / 1e3 * (w / base["world"]) for w in xs]
                ax.plot(xs, ideal, "--", alpha=0.5, label=f"{mode} (ideal)")
        ax.set_xlabel("GPUs (world size)")
        ax.set_ylabel("throughput (k tokens/s)")
        ax.set_title("Scaling")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        print(f"wrote {path}")


    def main():
        p = argparse.ArgumentParser()
        p.add_argument("patterns", nargs="*", default=["logs/*.log", "logs/*.out", "*.out"],
                       help="log files or globs to scan")
        p.add_argument("--csv", help="write results to this CSV path")
        p.add_argument("--plot", help="write a throughput-vs-GPUs plot (needs matplotlib)")
        args = p.parse_args()

        rows, files = parse_files(args.patterns)
        if not rows:
            print(f"No RESULT lines found in: {', '.join(files) or args.patterns}",
                  file=sys.stderr)
            sys.exit(1)

        add_scaling(rows)
        print(f"parsed {len(rows)} run(s) from {len(files)} file(s)\n")
        print_table(rows)
        if args.csv:
            write_csv(rows, args.csv)
        if args.plot:
            make_plot(rows, args.plot)


    if __name__ == "__main__":
        main()
    ```

---

## Adapting the example to your own work

- **Use real data.** Replace `get_batch()` with a `DataLoader` over your dataset. Keep `num_workers` and `pin_memory=True` so the loader keeps the GPUs fed — see [GPU Performance & Monitoring](gpu-performance.md#data-loading-optimization).
- **Grow the model.** Raise `--n-embd` / `--n-layer` until `peak mem (/GPU)` approaches ~120 GB. Add `--grad-checkpoint` to trade ~30% compute for a large activation-memory cut and fit a bigger batch.
- **Use FSDP for very large models.** `--parallel fsdp` shards parameters, gradients, and optimizer state across GPUs so a model too big for one GPU can still train.

!!! warning "FSDP shards parameters, not activations"
    FSDP splits the *weights* across GPUs, but each GPU still holds full-size *activations*. A wide model with a large batch can therefore still run out of memory under FSDP. For big-model tests, combine `--parallel fsdp` with `--grad-checkpoint` and/or a smaller `--micro-batch`.

---

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Job hangs at startup, never prints | Rendezvous failed. Check `MASTER_ADDR` resolves to the first node; try a different `MASTER_PORT` (e.g. `29600`) in case of a port conflict. |
| Multi-node run is slow; log shows `NET/Socket` | NCCL fell back to TCP. Confirm `NCCL_IB_DISABLE=0`, fix `NCCL_IB_HCA` (name from `ibstat`), and check `NCCL_SOCKET_IFNAME`. |
| Log has no `[GPUDirect RDMA]` even with `SYS` | The `nvidia-peermem` kernel module isn't loaded; GDR can't work without it. |
| `CUDA out of memory` | Lower `--micro-batch`, add `--grad-checkpoint`, or switch to `--parallel fsdp`. See [GPU memory optimization](gpu-performance.md#gpu-memory-optimization). |
| 2 GPUs barely faster than 1 | Expected to a degree on no-NVLink hardware. Make sure the step is compute-heavy enough (don't shrink the model); A/B test `NCCL_NET_GDR_LEVEL`. |
| One rank dies and the job hangs | This is what `TORCH_NCCL_ASYNC_ERROR_HANDLING=1` prevents — with it set, the job fails promptly. Then check every per-rank log for the real error. |

---

## Related Pages

- [GPU Computing on Juno](index.md) — GPU partitions, environment setup
- [GPU Performance & Monitoring](gpu-performance.md) — mixed precision, profiling, `nvidia-smi`, `jobstats`
- [Monitoring Jobs and Cluster State](../running-programs/advanced-slurm.md) — interpreting `jobstats` output
- [Containers](../advanced/containers.md) — running vLLM, AlphaFold, Stable Diffusion in containers
