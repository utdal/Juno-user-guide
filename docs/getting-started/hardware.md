# Hardware Overview

## Cluster Diagram

![Juno Cluster Diagram](../images/Juno.png)

## Node Types

Juno consists of **101 compute nodes** organized into four categories, plus login and head nodes.

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

## GPU Compute Nodes — NVIDIA A30

| Quantity | CPU | Cores/node | RAM | GPUs | GPU Memory | Network |
|----------|-----|------------|-----|------|------------|---------|
| 4 | 2× AMD EPYC 9534 2.45 GHz | 64C/128T per CPU → **128 cores total** | 1,024 GB | 2× A30 (physical, 24 GB each) | 24 GB | HDR100 InfiniBand, 2× 10/25 Gbps Ethernet |

A30 nodes also support virtual GPU slicing into 12 GB and 6 GB configurations.

## Available GPU Configurations

| Partition | GPU Type | Count | VRAM Each |
|-----------|----------|-------|-----------|
| `a30` | A30 physical | 2 per node | 24 GB |
| `a30-2.12gb` | A30 virtual (half) | 4 per node | 12 GB |
| `a30-4.6gb` | A30 virtual (quarter) | 8 per node | 6 GB |
| `h100` | H100 physical | 4 per node | 80 GB |
| `h100-94gb` | H100 physical (NVL) | 1 per node | 94 GB |
| `h100-2.47gb` | H100 virtual (half) | 4 per node | 47 GB |

## Network Infrastructure

All compute nodes are connected via **HDR100 InfiniBand** for low-latency, high-bandwidth MPI communication.

## Storage Systems

See [Storage and Data Transfer](storage.md) and [Scratch Space](scratch-space.md) for details on available storage systems.

| System | Path | Quota | Backup | Use For |
|--------|------|-------|--------|---------|
| Home (IO2) | `~` | 50 GB | Daily | Config files, scripts, small data |
| Work (IO2) | `~/work` | 1 TB | Daily | Large software, data, results |
| Group (IO2) | `/groups/<pi-name>` | 1 TB+ | Daily | Shared group data |
| Scratch | `~/scratch` | 30 TB | Never | High-speed I/O during batch jobs |

Scratch is up to **10× faster** for large I/O than home, work, or group directories.

## Next Steps

- [See available partitions and job limits →](../running-programs/slurm.md)
- [Storage and data management →](storage.md)
- [Request an account →](account-request.md)
