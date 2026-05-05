# Parallelism Models

## Introduction

Parallelism is the key to leveraging HPC clusters effectively. This guide covers different parallelism models available on Juno and when to use each approach.

## Why Parallelism?

### Benefits

**Faster execution**: Complete work in less time
**Larger problems**: Solve problems that don't fit on single machine
**Better resource utilization**: Use multiple cores/nodes efficiently
**Scalability**: Handle growing computational demands

## Types of Parallelism

### 1. Shared Memory Parallelism (OpenMP)

**Concept**: Multiple threads share the same memory space

**Best for**:
- Single-node parallel programs
- Loop parallelization
- Embarrassingly parallel tasks on one node
- Quick parallelization of existing code

**Not suitable for**:
- Multi-node programs
- Problems requiring distributed memory

### 2. Distributed Memory Parallelism (MPI)

**Concept**: Multiple processes with separate memory, communicate via message passing

**Best for**:
- Multi-node applications
- Large-scale parallel computing
- Problems requiring inter-process communication
- Scalable applications

**Not suitable for**:
- Simple single-node programs (overhead not worth it)
- Shared-state algorithms without explicit communication

### 3. Hybrid Parallelism (MPI + OpenMP)

**Concept**: Combines MPI across nodes with OpenMP within nodes

**Best for**:
- Large-scale computations
- Maximizing resource utilization
- Memory-intensive applications
- Modern cluster architectures

### 4. GPU Parallelism (CUDA)

**Concept**: Offload massively parallel computations to GPU

**Best for**:
- Data-parallel operations
- Matrix operations
- Deep learning
- Scientific simulations

## OpenMP (Shared Memory)

### Overview

OpenMP uses compiler directives to parallelize code with minimal changes.

### Basic Example

**C/C++**:
```c
#include <omp.h>
#include <stdio.h>

int main() {
    int nthreads, tid;
    
    #pragma omp parallel private(tid)
    {
        tid = omp_get_thread_num();
        printf("Hello from thread %d\n", tid);
        
        if (tid == 0) {
            nthreads = omp_get_num_threads();
            printf("Number of threads = %d\n", nthreads);
        }
    }
    return 0;
}
```

**Compile**:
```bash
module load gnu14
gcc -fopenmp hello_omp.c -o hello_omp
```

**Run**:
```bash
# Set number of threads
export OMP_NUM_THREADS=4
./hello_omp
```

### Parallel Loops

**C/C++**:
```c
#pragma omp parallel for
for (int i = 0; i < N; i++) {
    array[i] = compute(i);
}
```

**Fortran**:
```fortran
!$OMP PARALLEL DO
do i = 1, N
    array(i) = compute(i)
end do
!$OMP END PARALLEL DO
```

**Python (with Cython)**:
```python
from cython.parallel import prange

def parallel_function(double[:] array):
    cdef int i
    cdef int n = array.shape[0]
    
    for i in prange(n, nogil=True):
        array[i] = compute(i)
```

### Common OpenMP Directives

**Parallel region**:
```c
#pragma omp parallel
{
    // Code executed by all threads
}
```

**Parallel for**:
```c
#pragma omp parallel for
for (int i = 0; i < N; i++) {
    // Loop iterations distributed among threads
}
```

**Sections**:
```c
#pragma omp parallel sections
{
    #pragma omp section
    task1();
    
    #pragma omp section
    task2();
}
```

**Critical section** (mutex):
```c
#pragma omp critical
{
    // Only one thread at a time
    shared_variable += value;
}
```

**Reduction**:
```c
double sum = 0.0;
#pragma omp parallel for reduction(+:sum)
for (int i = 0; i < N; i++) {
    sum += array[i];
}
```

### SLURM Job Script for OpenMP

```bash
#!/bin/bash
#SBATCH -J openmp_job
#SBATCH -o output_%j.log
#SBATCH -e error_%j.log
#SBATCH -p normal
#SBATCH -N 1                    # Single node
#SBATCH -c 16                   # 16 CPUs
#SBATCH --mem=32GB
#SBATCH -t 2:00:00

# Load modules
module load gnu14

# Set number of threads
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Run program
./my_openmp_program
```

### OpenMP Environment Variables

```bash
export OMP_NUM_THREADS=8          # Number of threads
export OMP_PROC_BIND=true         # Bind threads to cores
export OMP_PLACES=cores           # Thread placement
export OMP_SCHEDULE="dynamic,4"   # Loop scheduling
```

## MPI (Distributed Memory)

### Overview

MPI (Message Passing Interface) enables parallel computing across multiple nodes.

### Basic Example

**C**:
```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    int rank, size;
    
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    printf("Hello from rank %d of %d\n", rank, size);
    
    MPI_Finalize();
    return 0;
}
```

**Compile**:
```bash
module load gnu14
module load openmpi5
mpicc hello_mpi.c -o hello_mpi
```

**Run**:
```bash
mpirun -np 4 ./hello_mpi
```

### Common MPI Operations

**Point-to-point communication**:
```c
// Send
MPI_Send(data, count, MPI_DOUBLE, dest, tag, MPI_COMM_WORLD);

// Receive
MPI_Recv(data, count, MPI_DOUBLE, source, tag, MPI_COMM_WORLD, &status);
```

**Collective communication**:
```c
// Broadcast
MPI_Bcast(data, count, MPI_DOUBLE, root, MPI_COMM_WORLD);

// Gather
MPI_Gather(sendbuf, sendcount, MPI_DOUBLE, 
           recvbuf, recvcount, MPI_DOUBLE, root, MPI_COMM_WORLD);

// Scatter
MPI_Scatter(sendbuf, sendcount, MPI_DOUBLE,
            recvbuf, recvcount, MPI_DOUBLE, root, MPI_COMM_WORLD);

// Reduce
MPI_Reduce(sendbuf, recvbuf, count, MPI_DOUBLE, 
           MPI_SUM, root, MPI_COMM_WORLD);

// All reduce
MPI_Allreduce(sendbuf, recvbuf, count, MPI_DOUBLE, 
              MPI_SUM, MPI_COMM_WORLD);
```

### SLURM Job Script for MPI

```bash
#!/bin/bash
#SBATCH -J mpi_job
#SBATCH -o output_%j.log
#SBATCH -e error_%j.log
#SBATCH -p normal
#SBATCH -N 4                    # 4 nodes
#SBATCH -n 64                   # 64 MPI tasks total
#SBATCH --mem=128GB             # Memory per node
#SBATCH -t 4:00:00

# Load modules
module load gnu14
module load openmpi5

# Run MPI program
mpirun -np $SLURM_NTASKS ./my_mpi_program
```

### MPI with SLURM

SLURM integrates with MPI:

```bash
# SLURM automatically sets these
$SLURM_NTASKS          # Total number of MPI tasks
$SLURM_NNODES          # Number of nodes
$SLURM_CPUS_PER_TASK   # CPUs per task

# Run with SLURM's srun (recommended)
srun ./my_mpi_program

# Or with mpirun
mpirun -np $SLURM_NTASKS ./my_mpi_program
```

## Hybrid MPI + OpenMP

### When to Use

- Large-scale simulations
- Memory-bound problems (fewer MPI ranks = more memory per rank)
- Modern multi-core nodes
- Reducing communication overhead

### Example Code

**C**:
```c
#include <mpi.h>
#include <omp.h>
#include <stdio.h>

int main(int argc, char** argv) {
    int rank, size, thread_num;
    
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    #pragma omp parallel private(thread_num)
    {
        thread_num = omp_get_thread_num();
        printf("MPI rank %d, OpenMP thread %d\n", rank, thread_num);
    }
    
    MPI_Finalize();
    return 0;
}
```

**Compile**:
```bash
module load gnu14
module load openmpi5
mpicc -fopenmp hybrid.c -o hybrid
```

### SLURM Job Script for Hybrid

```bash
#!/bin/bash
#SBATCH -J hybrid_job
#SBATCH -o output_%j.log
#SBATCH -e error_%j.log
#SBATCH -p normal
#SBATCH -N 4                    # 4 nodes
#SBATCH -n 16                   # 16 MPI ranks (4 per node)
#SBATCH -c 4                    # 4 OpenMP threads per MPI rank
#SBATCH --mem=128GB
#SBATCH -t 4:00:00

# Load modules
module load gnu14
module load openmpi5

# Set OpenMP threads
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Run hybrid program
srun ./hybrid_program
```

**Calculation**:
- 4 nodes × 4 MPI ranks per node = 16 total MPI ranks
- Each MPI rank uses 4 OpenMP threads
- Total: 64 CPU cores (16 × 4)

## GPU Parallelism

### CUDA Example

**CUDA kernel**:
```cuda
__global__ void vectorAdd(float *a, float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}

int main() {
    // Allocate and initialize arrays
    // ...
    
    // Copy to device
    cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);
    
    // Launch kernel
    int blockSize = 256;
    int numBlocks = (N + blockSize - 1) / blockSize;
    vectorAdd<<<numBlocks, blockSize>>>(d_a, d_b, d_c, N);
    
    // Copy result back
    cudaMemcpy(h_c, d_c, size, cudaMemcpyDeviceToHost);
    
    return 0;
}
```

**Compile**:
```bash
module unload gnu14
module load cuda/12.4
nvcc vector_add.cu -o vector_add
```

### SLURM Job Script for GPU

```bash
#!/bin/bash
#SBATCH -J gpu_job
#SBATCH -o output_%j.log
#SBATCH -e error_%j.log
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --gres=gpu:1            # Request 1 GPU
#SBATCH -c 4
#SBATCH --mem=16GB
#SBATCH -t 2:00:00

# Load modules
module load cuda/12.4

# Run GPU program
./my_gpu_program
```

## Python Parallelism

### Multiprocessing

**Shared memory parallelism**:
```python
from multiprocessing import Pool

def process_item(x):
    return x * x

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        results = pool.map(process_item, range(100))
```

### mpi4py

**MPI in Python**:
```python
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Hello from rank {rank} of {size}")

# Broadcast
data = None
if rank == 0:
    data = {'key': 'value'}
data = comm.bcast(data, root=0)

# Gather
local_data = rank * 2
all_data = comm.gather(local_data, root=0)
```

**SLURM job**:
```bash
#!/bin/bash
#SBATCH -J mpi4py_job
#SBATCH -p normal
#SBATCH -N 2
#SBATCH -n 8

module load python/3.9
module load openmpi/4.1

mpirun -np $SLURM_NTASKS python mpi_script.py
```

### Dask for Large Data

**Distributed computing**:
```python
from dask.distributed import Client
import dask.array as da

# Connect to cluster
client = Client()

# Distributed array
x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = x + x.T
result = y.mean().compute()
```

## Choosing the Right Model

### Decision Tree

```
Is your problem parallel?
├─ Yes
│  ├─ Fits on one node?
│  │  ├─ Yes → OpenMP
│  │  └─ No → MPI or Hybrid
│  ├─ Involves GPUs?
│  │  └─ Yes → CUDA/OpenCL
│  └─ Large data processing?
│     └─ Consider Dask/Spark
└─ No → Serial execution
```

### Comparison Table

| Model | Memory | Nodes | Complexity | Best For |
|-------|--------|-------|------------|----------|
| **OpenMP** | Shared | 1 | Low | Loop parallelism, single node |
| **MPI** | Distributed | Many | Medium | Multi-node, scalable apps |
| **Hybrid** | Both | Many | High | Large scale, memory-intensive |
| **GPU** | Device | 1-Many | High | Massively parallel, data-parallel |
| **Task-based** | Various | Various | Low | Independent tasks |

## Performance Considerations

### Scaling

**Strong scaling**: Fixed problem size, increase processors
- Goal: Reduce runtime
- Limited by Amdahl's Law

**Weak scaling**: Increase problem size with processors
- Goal: Maintain runtime
- Better scaling potential

### Amdahl's Law

```
Speedup = 1 / (S + P/N)

Where:
S = Serial fraction
P = Parallel fraction (P = 1 - S)
N = Number of processors
```

**Example**: If 10% of code is serial:
- 10 processors: max speedup = 5.3×
- 100 processors: max speedup = 9.2×
- ∞ processors: max speedup = 10×

### Communication Overhead

**Minimize communication**:
- Larger messages, fewer sends
- Overlap communication and computation
- Use collective operations when possible
- Consider communication topology

## Common Patterns

### Embarrassingly Parallel

**No communication needed**:
```python
# Example: Monte Carlo simulation
from multiprocessing import Pool

def run_simulation(seed):
    return monte_carlo(seed)

with Pool(processes=8) as pool:
    results = pool.map(run_simulation, range(1000))
```

### Master-Worker

**Dynamic load balancing**:
```c
// Master distributes tasks
if (rank == 0) {
    for (int i = 0; i < ntasks; i++) {
        MPI_Recv(&result, 1, MPI_INT, MPI_ANY_SOURCE, 
                 TAG_RESULT, MPI_COMM_WORLD, &status);
        int worker = status.MPI_SOURCE;
        MPI_Send(&task[i], 1, MPI_INT, worker, 
                 TAG_TASK, MPI_COMM_WORLD);
    }
}
// Workers process tasks
else {
    while (1) {
        MPI_Recv(&task, 1, MPI_INT, 0, TAG_TASK, 
                 MPI_COMM_WORLD, &status);
        result = process(task);
        MPI_Send(&result, 1, MPI_INT, 0, TAG_RESULT, 
                 MPI_COMM_WORLD);
    }
}
```

### Stencil Computation

**Nearest-neighbor communication**:
```c
// Ghost cell exchange in MPI
MPI_Sendrecv(send_left, n, MPI_DOUBLE, left_rank, 0,
             recv_right, n, MPI_DOUBLE, right_rank, 0,
             MPI_COMM_WORLD, &status);
             
MPI_Sendrecv(send_right, n, MPI_DOUBLE, right_rank, 0,
             recv_left, n, MPI_DOUBLE, left_rank, 0,
             MPI_COMM_WORLD, &status);
```

## Debugging Parallel Programs

### Common Issues

**Race conditions**:
```c
// Bad (race condition)
for (int i = 0; i < N; i++) {
    sum += array[i];  // Multiple threads modify sum
}

// Good (use reduction)
#pragma omp parallel for reduction(+:sum)
for (int i = 0; i < N; i++) {
    sum += array[i];
}
```

**Deadlocks**:
```c
// Bad (can deadlock)
MPI_Send(data, n, MPI_INT, partner, 0, MPI_COMM_WORLD);
MPI_Recv(data, n, MPI_INT, partner, 0, MPI_COMM_WORLD, &status);

// Good (use Sendrecv or non-blocking)
MPI_Sendrecv(sendbuf, n, MPI_INT, partner, 0,
             recvbuf, n, MPI_INT, partner, 0,
             MPI_COMM_WORLD, &status);
```

### Debugging Tools

**GDB with MPI**:
```bash
mpirun -np 4 xterm -e gdb ./program
```

**Valgrind**:
```bash
mpirun -np 4 valgrind ./program
```

**Print debugging**:
```c
if (rank == 0) {
    printf("Debug info: %d\n", value);
}
```

## Best Practices

### 1. Start Small

- Test with small problem sizes
- Verify correctness before scaling
- Profile serial code first

### 2. Measure Performance

```bash
# Time your program
time ./program

# Use profiling tools
gprof ./program
```

### 3. Test Scaling

```bash
# Test with increasing core counts
for n in 1 2 4 8 16; do
    mpirun -np $n ./program
done
```

### 4. Optimize Communication

- Minimize communication frequency
- Use non-blocking operations
- Overlap computation and communication

### 5. Balance Load

- Ensure even work distribution
- Use dynamic scheduling for irregular workloads
- Monitor per-process resource usage

## Resources and Examples

### Example Repositories

Check HPC website for example codes:
- OpenMP examples
- MPI tutorials
- Hybrid applications
- GPU kernels

### Learning Resources

**OpenMP**:
- [openmp.org/resources](https://www.openmp.org/resources/)
- Tutorial: [hpc-tutorials.llnl.gov/openmp](https://hpc-tutorials.llnl.gov/openmp/)

**MPI**:
- [mpi-forum.org](https://www.mpi-forum.org/)
- Tutorial: [mpitutorial.com](https://mpitutorial.com/)

**CUDA**:
- [developer.nvidia.com/cuda-zone](https://developer.nvidia.com/cuda-zone)

## Next Steps

- [High throughput computing →](launcher.md)
- [Optimize Python code →](../advanced/python-optimization.md)
- [Use containers for complex dependencies →](../advanced/containers.md)

## Need Help?

- **Parallelization advice**: Request consultation via [support ticket](../support/getting-help.md)
- **Code optimization**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **MPI/OpenMP issues**: Include code snippet and error in ticket