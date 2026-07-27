# Hardware Overview

## Overview

This page describes Juno's physical hardware: the overall cluster layout, the different node types (login and head nodes, the four categories of compute node, and the GPU nodes), and the CPUs, memory, networking, and storage that make up each. Use it to understand what resources are available and to choose the right node type and partition for your jobs.

## Cluster Diagram

![Juno Cluster Diagram](../images/Juno.png)

## Node Types

Juno consists of **127 compute nodes** — CPU compute nodes plus H100, A30, and [H200](#gpu-compute-nodes-nvidia-h200) GPU nodes — along with login and head nodes.

## Login and Head Nodes

| Quantity | CPU | Cores/node | RAM | Storage | Network |
|----------|-----|------------|-----|---------|---------|
| 3 | 2× Intel Xeon Silver 4309Y 2.8 GHz | 8C/16T | 128–384 GB | 3.84 TB SSD (2× 1.92 TB) | HDR100 InfiniBand, 2× 1 Gbps Ethernet |

These nodes handle login sessions, job submission, and cluster management. **Do not run computational work on login nodes.**

## CPU Compute Nodes

| Quantity | CPU | Cores/node | RAM | Storage | Network |
|----------|-----|------------|-----|---------|---------|
| 94 | 2× AMD EPYC 9334 2.7 GHz | 32C/64T per CPU → **64 cores total** | 384 GB | 480 GB SSD | HDR100 InfiniBand, 10/25 Gbps Ethernet |

These are the standard compute nodes used for most CPU-based workloads. Submit jobs to the `normal` or `dev` partitions.

## GPU Compute Nodes — NVIDIA H100

| Quantity | CPU | Cores/node | RAM | GPUs | GPU Memory | Network |
|----------|-----|------------|-----|------|------------|---------|
| 1 | 2× Intel Xeon Platinum 8462Y 2.8 GHz | 32C/64T per CPU → **64 cores total** | 512 GB | 4× H100 (physical, 80 GB HBM3 each) | 80 GB | HDR100 InfiniBand, 2× 10/25 Gbps Ethernet |
| 1 | 2× Intel Xeon Platinum 8462Y 2.8 GHz | 64 cores total | 512 GB | 2× H100 (physical, 94 GB NVL) | 94 GB | HDR100 InfiniBand |
| 1 | 2× Intel Xeon Platinum 8462Y 2.8 GHz | 64 cores total | 512 GB | 1× H100 (physical, 94 GB NVL) | 94 GB | HDR100 InfiniBand |

H100 nodes also support **virtual GPU slicing** — a single physical H100 can be split into multiple virtual GPUs. See the [SLURM partitions table](../running-programs/slurm.md#partitions-overview) for available GPU configurations.

!!! note "NVLink is only on `g-04-02`"
    Only the **4× H100 (80 GB HBM3)** node, `g-04-02`, has **NVLink** for fast direct GPU-to-GPU communication. Despite the "NVL" in their product name, the 94 GB H100 NVL nodes do **not** have NVLink bridges installed, and the A30 nodes have no NVLink either — on all other nodes, GPUs communicate over PCIe. This matters for multi-GPU jobs (see [PyTorch Training Tutorial](../ai-and-ml/pytorch-training.md)).

## GPU Compute Nodes — NVIDIA A30

| Quantity | CPU | Cores/node | RAM | GPUs | GPU Memory | Network |
|----------|-----|------------|-----|------|------------|---------|
| 4 | 2× AMD EPYC 9534 2.45 GHz | 64C/128T per CPU → **128 cores total** | 1,024 GB | 2× A30 (physical, 24 GB each) | 24 GB | HDR100 InfiniBand, 2× 10/25 Gbps Ethernet |

A30 nodes also support virtual GPU slicing into 12 GB and 6 GB configurations.

## GPU Compute Nodes — NVIDIA H200

!!! note "Available"
    The H200 nodes are online and the `h200` partition is available. See [GPU Computing on Juno](../ai-and-ml/index.md).

| Quantity | CPU | Cores/node | RAM | GPUs | GPU Memory | Network |
|----------|-----|------------|-----|------|------------|---------|
| 26 | 2× AMD EPYC 9335 3.0 GHz | 32C/32T per CPU → **64 cores total** | 384 GB | 2× H200 NVL (141 GB each) | 141 GB | 400 Gb InfiniBand (NDR), PCIe Gen 5.0 |

H200 NVL cards have **no NVLink** — GPUs communicate over PCIe Gen 5.0 within a node and over 400 Gb InfiniBand between nodes.

## Available GPU Configurations

| Partition | GPU Type | Count | VRAM Each |
|-----------|----------|-------|-----------|
| `a30` | A30 physical | 2 per node | 24 GB |
| `a30-2.12gb` | A30 virtual (half) | 4 per node | 12 GB |
| `a30-4.6gb` | A30 virtual (quarter) | 8 per node | 6 GB |
| `h100` | H100 physical / virtual | 4× (80 GB), 1× (94 GB NVL), or 4× half-slice (47 GB) | 80 / 94 / 47 GB |
| `h200` | H200 NVL | 2 per node | 141 GB |

![GPU virtual slicing — a physical A30 or H100 can be divided into multiple virtual GPUs, each with a smaller VRAM slice, for concurrent lightweight workloads.](../images/hardware-gpu-slicing.png)

## Network Infrastructure

The CPU, A30, and H100 compute nodes are connected via **HDR100 InfiniBand (100 Gb/s)** for low-latency, high-bandwidth MPI communication, and use **PCIe Gen 4.0** for device (GPU and network card) attachment.

The H200 nodes use faster interconnects: **400 Gb InfiniBand (NDR)** between nodes and **PCIe Gen 5.0** for device attachment.

## Storage Systems

See [Storage and Data Transfer](storage.md) and [Scratch Space](scratch-space.md) for details on available storage systems.

| System | Path | Quota | Backup | Shared with G2 | Use For |
|--------|------|-------|--------|----------------|---------|
| Home (Io) | `~` | 50 GB | Daily | No | Config files, scripts, small data |
| Work (Io) | `~/work` | 1 TB | Daily | No (Juno only) | Large software, data, results |
| Group (Io) | `/groups/<pi-name>` | 1 TB+ | Daily | **Yes** | Shared group data |
| Scratch | `~/scratch` | 30 TB | Never | **Yes** | High-speed I/O during batch jobs |

Scratch is up to **10× faster** for large I/O than home, work, or group directories.

`/groups/<pi-name>` and `~/scratch` are the **same filesystems as on Ganymede 2** — see [Shared with Ganymede 2](storage.md#storage-systems-on-juno).

## Next Steps

- [See available partitions and job limits →](../running-programs/slurm.md)
- [Storage and data management →](storage.md)
- [Request an account →](account-request.md)
