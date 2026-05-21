# Parallelism Models

## Introduction

Parallelism is the key to using an HPC cluster effectively. This page explains the parallelism models available on Juno, when to use each, and how to compile and submit jobs for them. It focuses on the Juno-specific mechanics — for the APIs themselves, links to upstream tutorials are provided at the end.

## Choosing a Model

```
Is your problem parallel?
├─ Yes
│  ├─ Fits on one node?
│  │  ├─ Yes → OpenMP (threads) or multiprocessing
│  │  └─ No  → MPI or Hybrid (MPI + OpenMP)
│  ├─ Involves GPUs?       → CUDA / CuPy / PyTorch
│  └─ Many independent tasks? → Job arrays or Launcher
└─ No → Serial execution
```

| Model | Memory | Nodes | Best for |
|-------|--------|-------|----------|
| **OpenMP** | Shared | 1 | Loop parallelism on a single node |
| **MPI** | Distributed | Many | Multi-node, scalable applications |
| **Hybrid (MPI+OpenMP)** | Both | Many | Large-scale, memory-intensive runs |
| **GPU (CUDA)** | Device | 1–many | Massively data-parallel work |
| **Task-based** | Various | Various | Many independent tasks — see [Launcher](launcher.md) |

---

## 1. Shared Memory Parallelism (OpenMP)

Multiple threads share one address space on a **single node**. Best for loop parallelization and quick parallelization of existing code; not usable across nodes.

```
  Single Node  (#SBATCH -N 1  -c 16  +  export OMP_NUM_THREADS=16)
  ┌────────────────────────────────────────────────────────────────┐
  │  Thread 0    Thread 1    Thread 2   ...   Thread N-1           │
  │  ┌────────┐  ┌────────┐  ┌────────┐      ┌────────┐           │
  │  │ core 0 │  │ core 1 │  │ core 2 │      │ core N │           │
  │  └───┬────┘  └───┬────┘  └───┬────┘      └───┬────┘           │
  │      └───────────┴───────────┴───────────────┘                 │
  │                  ┌────────────────────────┐                    │
  │                  │     Shared Memory      │                    │
  │                  │   (one address space)  │                    │
  │                  └────────────────────────┘                    │
  └────────────────────────────────────────────────────────────────┘
  All threads read/write the same memory — no network communication.
```

**Compile and run on Juno:**

```bash
module load gnu14
gcc -fopenmp my_program.c -o my_program     # gfortran -fopenmp for Fortran
```

```bash
#!/bin/bash
#SBATCH -J openmp_job
#SBATCH -o output_%j.log
#SBATCH -p normal
#SBATCH -N 1                    # single node
#SBATCH -c 16                   # 16 CPUs
#SBATCH --mem=32GB
#SBATCH -t 2:00:00

module load gnu14

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK   # match threads to allocated cores
./my_program
```

Useful tuning variables: `OMP_PROC_BIND=true` and `OMP_PLACES=cores` (bind threads to cores), `OMP_SCHEDULE="dynamic,4"` (loop scheduling).

---

## 2. Distributed Memory Parallelism (MPI)

Multiple processes (ranks), each with **private memory**, communicate by passing messages over Juno's HDR100 InfiniBand. Best for multi-node, scalable applications.

```
  Node 1          Node 2          Node 3          Node 4
  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
  │  Rank 0    │  │  Rank 1    │  │  Rank 2    │  │  Rank 3    │
  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │
  │ │Memory 0│ │  │ │Memory 1│ │  │ │Memory 2│ │  │ │Memory 3│ │
  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │
  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
        └───────────────┴───────────────┴───────────────┘
                         HDR100 InfiniBand
  Each process has private memory — data must be explicitly sent.
  (#SBATCH -N 4  -n 64  →  srun ./my_mpi_program)
```

**Compile and run on Juno:**

```bash
module load gnu14 openmpi5
mpicc my_mpi_program.c -o my_mpi_program    # mpif90 for Fortran
```

```bash
#!/bin/bash
#SBATCH -J mpi_job
#SBATCH -o output_%j.log
#SBATCH -p normal
#SBATCH -N 4                    # 4 nodes
#SBATCH -n 64                   # 64 MPI tasks total
#SBATCH --mem=128GB             # per node
#SBATCH -t 4:00:00

module load gnu14 openmpi5

srun ./my_mpi_program           # srun is preferred; mpirun -np $SLURM_NTASKS also works
```

SLURM sets `$SLURM_NTASKS`, `$SLURM_NNODES`, and `$SLURM_CPUS_PER_TASK` for you — use these instead of hard-coding counts.

---

## 3. Hybrid Parallelism (MPI + OpenMP)

Combines MPI **across** nodes with OpenMP **within** each node. Fewer MPI ranks means more memory per rank and less communication overhead — well suited to Juno's many-core nodes.

```
  Node 1                                Node 2
  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
  │  MPI Rank 0                     │   │  MPI Rank 1                     │
  │  ┌───────┬───────┬───────┬──────┐│  │  ┌───────┬───────┬───────┬──────┐│
  │  │ thd 0 │ thd 1 │ thd 2 │thd 3 ││  │  │ thd 0 │ thd 1 │ thd 2 │thd 3 ││
  │  └───────┴───────┴───────┴──────┘│  │  └───────┴───────┴───────┴──────┘│
  │        OpenMP shared memory       │  │        OpenMP shared memory       │
  └────────────────┬────────────────┘   └────────────────┬────────────────┘
                   └──────────── MPI messages ────────────┘
                                 (InfiniBand)
```

```bash
module load gnu14 openmpi5
mpicc -fopenmp hybrid.c -o hybrid
```

```bash
#!/bin/bash
#SBATCH -J hybrid_job
#SBATCH -p normal
#SBATCH -N 4                    # 4 nodes
#SBATCH -n 16                   # 16 MPI ranks (4 per node)
#SBATCH -c 4                    # 4 OpenMP threads per rank
#SBATCH --mem=128GB
#SBATCH -t 4:00:00

module load gnu14 openmpi5

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
srun ./hybrid                   # 16 ranks × 4 threads = 64 cores total
```

---

## 4. GPU Parallelism (CUDA)

Offload massively data-parallel work to a GPU. Best for dense linear algebra, deep learning, and large simulations.

**Compile and run on Juno:**

```bash
module load cuda/12.6
nvcc vector_add.cu -o vector_add
```

```bash
#!/bin/bash
#SBATCH -J gpu_job
#SBATCH -p h100                 # or a30
#SBATCH -N 1
#SBATCH --gres=gpu:1            # request 1 GPU
#SBATCH -c 4
#SBATCH --mem=16GB
#SBATCH -t 2:00:00

module load cuda/12.6
./vector_add
```

For GPU work in Python (PyTorch, CuPy, Numba) see [GPU Computing on Juno](../ai-and-ml/index.md) and [Accelerating Python](../advanced/python-optimization.md).

---

## Python Parallelism

Python has its own parallelism options — `multiprocessing`, `joblib`, `mpi4py`, and Dask. These are covered, with examples and SLURM scripts, in [Accelerating Python](../advanced/python-optimization.md).

---

## Performance Considerations

- **Strong scaling**: fixed problem size, more processors → lower runtime (bounded by **Amdahl's Law**: if a fraction `S` of the code is serial, maximum speedup is `1 / S`, regardless of processor count).
- **Weak scaling**: grow the problem size with the processor count → maintain runtime. Generally scales better.
- **Minimize communication**: prefer fewer, larger messages; use collective operations; overlap communication with computation.
- **Test scaling before committing**: benchmark at 1, 2, 4, 8… cores/nodes and confirm you get real speedup before requesting large allocations. Use [`jobstats`](advanced-slurm.md#job-efficiency-jobstats) to check efficiency.

To run a job on more than the default 8 nodes, [contact support](../support/getting-help.md) with evidence of efficient scaling.

---

## Learning the APIs

This page covers how to build and run parallel jobs on Juno. For the programming APIs themselves:

- **OpenMP**: [openmp.org/resources](https://www.openmp.org/resources/), [LLNL OpenMP tutorial](https://hpc-tutorials.llnl.gov/openmp/)
- **MPI**: [mpitutorial.com](https://mpitutorial.com/), [MPI Forum](https://www.mpi-forum.org/)
- **CUDA**: [NVIDIA CUDA Zone](https://developer.nvidia.com/cuda-zone)

## Next Steps

- [High throughput with Launcher →](launcher.md)
- [Accelerating Python →](../advanced/python-optimization.md)
- [GPU Computing on Juno →](../ai-and-ml/index.md)

## Need Help?

- **Parallelization advice**: request a [consultation](../support/getting-help.md)
- **MPI/OpenMP issues**: include a code snippet and the error in your ticket
