# Accelerating Python on HPC Clusters

## Introduction

Python is popular for scientific computing but can be slow for large-scale computations. This guide covers strategies to accelerate Python code on Juno.

## Understanding Python Performance

### Why is Python Slow?

- **Interpreted language**: No compile-time optimization
- **Dynamic typing**: Runtime type checking overhead
- **Global Interpreter Lock (GIL)**: Limits true parallelism
- **Memory overhead**: Object-based everything

### When to Optimize

1. **Profile first**: Identify bottlenecks
2. **Algorithm matters most**: O(n²) → O(n log n) beats micro-optimizations
3. **Use right tools**: NumPy/SciPy for numerical work
4. **Parallelize**: Utilize multiple cores/nodes

## Profiling Python Code

### Time Measurement

**Basic timing**:
```python
import time

start = time.time()
result = expensive_function()
end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
```

**IPython magic**:
```python
# Time single line
%time result = expensive_function()

# Time with multiple runs
%timeit expensive_function()

# Time entire cell
%%time
# multiple lines
# of code
```

### cProfile

**Profile entire script**:
```bash
python -m cProfile -s cumulative script.py
```

**In code**:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### line_profiler

**Install**:
```bash
pip install line_profiler
```

**Usage**:
```python
# Add @profile decorator
@profile
def expensive_function():
    # code here
    pass
```

**Run**:
```bash
kernprof -l -v script.py
```

## Vectorization with NumPy

### Avoid Python Loops

**Slow (Python loop)**:
```python
import numpy as np

data = np.random.rand(1000000)
result = np.zeros(len(data))

for i in range(len(data)):
    result[i] = data[i] ** 2 + 2 * data[i] + 1
```

**Fast (NumPy vectorized)**:
```python
import numpy as np

data = np.random.rand(1000000)
result = data**2 + 2*data + 1  # ~100x faster
```

### NumPy Operations

**Element-wise operations**:
```python
# All operate on entire arrays at once
a + b          # Addition
a * b          # Multiplication
np.sin(a)      # Trigonometric
np.exp(a)      # Exponential
a > 0          # Boolean operations
```

**Broadcasting**:
```python
# Operates on arrays of different shapes
a = np.array([[1, 2, 3],
              [4, 5, 6]])
b = np.array([10, 20, 30])

c = a + b  # Broadcasts b to each row
# [[11, 22, 33],
#  [14, 25, 36]]
```

**Reduction operations**:
```python
data.sum()           # Sum all elements
data.mean()          # Mean
data.std()           # Standard deviation
data.min()           # Minimum
data.argmax()        # Index of maximum
```

**Multithreading**:
As NumPy is primarily written in C and Fortran, your program may benefit from multithreading speedup.

```python
# Matrix multiplication with multithreading
import numpy as np
import time

# Matrix size
N = 2048

# Create random matrices
A = np.random.rand(N, N).astype(np.float32)
B = np.random.rand(N, N).astype(np.float32)

# Time the multiplication
start = time.time()
C = A @ B
end = time.time()

print(f"NumPy matrix multiplication took {end - start:.4f} seconds")

```

```bash
# Running on 4 CPU cores
export OMP_NUM_THREADS=4
python matrix_multiplication.py

```

| Number of CPU cores (threads) | Execution time (s) |
|---|---|
| 1 | 0.1537 |
| 2 | 0.0831 |
| 4 | 0.0464 |
| 8 | 0.0253 |
| 16 | 0.0142 |
| 32 | 0.0081 |
| 64 | 0.0060 |

Example SLURM script:

```bash
#SBATCH -N 1
#SBATCH --cpus-per-task=64
#SBATCH -p normal
#SBATCH --mem=5GB
#SBATCH --time=00:10:00

module load miniconda
conda activate /path/to/env
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
python matrix_multiplication.py

```

## Optimized Libraries

### Use Compiled Libraries

**NumPy/SciPy** (use system-optimized versions):
```bash
module load python/3.12.2
# NumPy linked with optimized BLAS (MKL or OpenBLAS)

python -c "import numpy; numpy.show_config()"
```

**Pandas** for data manipulation:
```python
import pandas as pd

# Fast operations on DataFrames
df = pd.read_csv('data.csv')
result = df.groupby('category')['value'].mean()
```

**Scikit-learn** for machine learning:
```python
from sklearn.ensemble import RandomForestClassifier

# Optimized implementations
clf = RandomForestClassifier(n_jobs=-1)  # Use all cores
clf.fit(X_train, y_train)
```

## Numba: JIT Compilation

### Basic Usage

**Install**:
```bash
pip install --user numba
```

**Simple example**:
```python
from numba import jit
import numpy as np

@jit(nopython=True)
def fast_function(x):
    total = 0.0
    for i in range(x.shape[0]):
        total += x[i] ** 2
    return total

data = np.random.rand(1000000)
result = fast_function(data)  # Near C speed
```

### Parallel Execution

```python
from numba import jit, prange

@jit(nopython=True, parallel=True)
def parallel_function(x):
    n = x.shape[0]
    result = np.zeros(n)
    for i in prange(n):  # Parallel loop
        result[i] = expensive_computation(x[i])
    return result
```

### NumPy Functions

```python
import numpy as np
from numba import jit

@jit(nopython=True)
def numba_with_numpy(arr):
    return np.sum(arr ** 2)  # NumPy works with Numba
```

## Cython: Python with C Performance

### Basic Cython

**Create .pyx file** (`fast_code.pyx`):
```python
# cython: language_level=3
import numpy as np
cimport numpy as np

def fast_loop(double[:] data):
    cdef int i
    cdef int n = data.shape[0]
    cdef double total = 0.0
    
    for i in range(n):
        total += data[i] ** 2
    
    return total
```

**Setup file** (`setup.py`):
```python
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize("fast_code.pyx"),
    include_dirs=[numpy.get_include()]
)
```

**Compile**:
```bash
python setup.py build_ext --inplace
```

**Use**:
```python
import fast_code
import numpy as np

data = np.random.rand(1000000)
result = fast_code.fast_loop(data)
```

## Parallel Processing

### Multiprocessing

**Basic parallelism**:
```python
from multiprocessing import Pool
import numpy as np

def process_chunk(data):
    return np.sum(data ** 2)

if __name__ == '__main__':
    data = np.random.rand(1000000)
    chunks = np.array_split(data, 8)
    
    with Pool(processes=8) as pool:
        results = pool.map(process_chunk, chunks)
    
    total = sum(results)
```

**SLURM job**:
```bash
#!/bin/bash
#SBATCH -J multiproc
#SBATCH -c 16
#SBATCH --mem=32GB
#SBATCH -t 2:00:00

module load python/3.12.2

# Python will use $SLURM_CPUS_PER_TASK cores
python parallel_script.py
```

### Joblib

```python
from joblib import Parallel, delayed

def process_item(x):
    return expensive_computation(x)

# Process in parallel
results = Parallel(n_jobs=8)(
    delayed(process_item)(x) for x in data
)
```

### Dask for Big Data

**Distributed computing**:
```python
import dask.array as da
import dask.dataframe as dd

# Large array operations
x = da.random.random((10000, 10000), chunks=(1000, 1000))
result = (x + x.T).mean().compute()

# Large DataFrames
df = dd.read_csv('huge_file.csv')
result = df.groupby('category')['value'].mean().compute()
```

**SLURM job with Dask**:
```bash
#!/bin/bash
#SBATCH -N 2
#SBATCH -n 32
#SBATCH -t 4:00:00

module load python/3.12.2

python dask_script.py
```

**Dask script**:
```python
from dask.distributed import Client
from dask_jobqueue import SLURMCluster

cluster = SLURMCluster(
    cores=16,
    memory='64GB',
    processes=16,
    walltime='04:00:00'
)
cluster.scale(jobs=2)

client = Client(cluster)

# Your Dask computations
```

## MPI with Python (mpi4py)

### Installation

```bash
module load python/3.12.2
module load openmpi5
pip install --user mpi4py
```

### Basic Example

```python
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Each process gets part of the data
data = np.random.rand(1000000) if rank == 0 else None

# Scatter data
local_data = np.empty(1000000 // size)
comm.Scatter(data, local_data, root=0)

# Process locally
local_result = np.sum(local_data ** 2)

# Gather results
results = comm.gather(local_result, root=0)

if rank == 0:
    total = sum(results)
    print(f"Total: {total}")
```

**SLURM job**:
```bash
#!/bin/bash
#SBATCH -N 2
#SBATCH -n 16
#SBATCH -t 2:00:00

module load python/3.12.2
module load openmpi5

mpirun -np $SLURM_NTASKS python mpi_script.py
```

## GPU Acceleration

For data-parallel workloads, moving arrays to a GPU can give large speedups. The main options in Python are **CuPy** (a drop-in NumPy replacement), **Numba** (`@cuda.jit` kernels), and **PyTorch**:

```python
import cupy as cp
x_gpu = cp.random.rand(1_000_000)
result = cp.asnumpy(cp.sum(x_gpu ** 2))   # compute on GPU, copy back
```

Setup, GPU partitions, library installation, profiling, and memory tuning for GPU work are covered in detail in the AI & ML section:

- [GPU Computing on Juno](../ai-and-ml/index.md) — environment setup and partitions
- [GPU Performance & Monitoring](../ai-and-ml/gpu-performance.md) — CuPy, Numba, vLLM, and memory optimization

## Memory Optimization

### Efficient Data Types

```python
import numpy as np

# Bad: Default float64 (8 bytes per element)
data = np.random.rand(1000000)

# Good: float32 (4 bytes per element) if precision allows
data = np.random.rand(1000000).astype(np.float32)

# Even better for integers
data = np.random.randint(0, 100, 1000000, dtype=np.int8)
```

### Memory-Mapped Files

```python
import numpy as np

# Create memory-mapped array
data = np.memmap('data.mmap', dtype='float32', mode='w+', 
                 shape=(1000000, 100))

# Write data
data[:] = np.random.rand(1000000, 100)

# Later, load without loading entire file into memory
data = np.memmap('data.mmap', dtype='float32', mode='r',
                 shape=(1000000, 100))
```

### Chunked Processing

```python
import pandas as pd

# Process large file in chunks
chunk_size = 100000
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    # Process each chunk
    result = process(chunk)
    save_result(result)
```

## I/O Optimization

### Efficient File Formats

```python
import numpy as np
import pandas as pd

# NumPy binary (fast)
np.save('data.npy', array)
array = np.load('data.npy')

# HDF5 (good for large datasets)
import h5py
with h5py.File('data.h5', 'w') as f:
    f.create_dataset('dataset', data=array)

# Parquet (good for DataFrames)
df.to_parquet('data.parquet')
df = pd.read_parquet('data.parquet')
```

### Parallel I/O

```python
import pandas as pd
from multiprocessing import Pool

def read_file(filename):
    return pd.read_csv(filename)

files = ['file1.csv', 'file2.csv', 'file3.csv']

with Pool(4) as pool:
    dataframes = pool.map(read_file, files)

combined = pd.concat(dataframes)
```

## Best Practices

### 1. Choose Right Tool

```python
# Simple numerical operations → NumPy
result = np.sum(data ** 2)

# Complex loops with conditions → Numba
@jit(nopython=True)
def complex_calculation(data):
    # complex logic
    pass

# Large-scale parallel → mpi4py or Dask
# GPU operations → CuPy or PyTorch
```

### 2. Profile Before Optimizing

```bash
# Profile
python -m cProfile -o output.prof script.py

# Visualize
python -m pstats output.prof
```

### 3. Vectorize First

```python
# Instead of loops
result = []
for x in data:
    result.append(x ** 2)

# Use vectorization
result = data ** 2
```

### 4. Use Appropriate Data Structures

```python
# Lists: Flexible but slow
# NumPy arrays: Fast for numerical operations
# Pandas DataFrames: Good for structured data
# Dictionaries: Fast lookups
```

## Complete Example

### Serial vs Parallel Comparison

```python
import numpy as np
from numba import jit, prange
from multiprocessing import Pool
import time

# Serial Python
def slow_computation(data):
    result = []
    for x in data:
        result.append(x ** 2 + 2 * x + 1)
    return result

# NumPy vectorized
def numpy_computation(data):
    return data ** 2 + 2 * data + 1

# Numba JIT
@jit(nopython=True)
def numba_computation(data):
    result = np.empty(len(data))
    for i in range(len(data)):
        result[i] = data[i] ** 2 + 2 * data[i] + 1
    return result

# Numba parallel
@jit(nopython=True, parallel=True)
def numba_parallel(data):
    result = np.empty(len(data))
    for i in prange(len(data)):
        result[i] = data[i] ** 2 + 2 * data[i] + 1
    return result

# Test
data = np.random.rand(10000000)

# Serial
t0 = time.time()
result1 = slow_computation(data)
t1 = time.time()
print(f"Serial Python: {t1-t0:.2f}s")

# NumPy
t0 = time.time()
result2 = numpy_computation(data)
t1 = time.time()
print(f"NumPy: {t1-t0:.2f}s")

# Numba
t0 = time.time()
result3 = numba_computation(data)
t1 = time.time()
print(f"Numba: {t1-t0:.2f}s")

# Numba parallel
t0 = time.time()
result4 = numba_parallel(data)
t1 = time.time()
print(f"Numba parallel: {t1-t0:.2f}s")
```

## Common Pitfalls

### 1. Premature Optimization

**Don't**:

- Optimize before profiling
- Sacrifice readability for minor gains
- Over-engineer simple problems

### 2. Wrong Tool

**Don't**:

- Use Cython for everything (NumPy often enough)
- Parallelize serial bottlenecks
- Use GPU for small data

### 3. Memory Issues

**Watch for**:

- Copying large arrays unnecessarily
- Creating temporary arrays in loops
- Not using appropriate data types

## Quick Reference

### Speed Comparison

```
Pure Python loops:      1x (baseline)
List comprehensions:    1.5x
NumPy vectorized:       50-100x
Numba JIT:             50-100x
Numba parallel:        100-500x (depends on cores)
Cython:                50-500x
MPI (multi-node):      scales with nodes
GPU:                   100-1000x (for suitable problems)
```

### When to Use What

| Approach | Best For |
|----------|----------|
| **NumPy** | Array operations, linear algebra |
| **Numba** | Loops with logic, numerical code |
| **Cython** | Integration with C libraries |
| **Multiprocessing** | CPU-bound independent tasks |
| **MPI** | Large-scale distributed computing |
| **Dask** | Big data, out-of-core computation |
| **GPU** | Massively parallel operations |

## Next Steps

- [Set up Miniconda environments →](miniconda.md)
- [Use containers for dependencies →](containers.md)
- [Learn parallelism models →](../running-programs/parallelism.md)

## Need Help?

- **Optimization consultation**: Request via [support ticket](../support/getting-help.md)
- **Python issues**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Package installation**: Open software installation ticket