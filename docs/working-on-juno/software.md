# Software and Compilers Available on Juno

## Overview

This page provides information about software and compilers available on Juno, how to access them, and how to request new software installations.

## Finding Available Software

### Using the Module System

```bash
# List all available software
module avail

# Search for specific software
module avail python
module avail gnu14
module avail matlab

# Case-insensitive search
module avail -i tensorflow
```

See the [Module System Guide](modules.md) for detailed usage.

## Categories of Software

### Compilers

#### GNU Compiler

**Languages**: C, C++, Fortran

```bash
# Available versions
module avail gnu

# Load GNU
module load gnu14

# Verify
gcc --version
g++ --version
gfortran --version
```

**Compile examples**:
```bash
# C program
gcc -O3 program.c -o program

# C++ program
g++ -O3 program.cpp -o program

# Fortran program
gfortran -O3 program.f90 -o program
```

#### Intel Compilers

**Languages**: C, C++, Fortran (optimized for Intel processors)

```bash
# Load Intel compilers
module load intel/2025

# Use
icc program.c -o program      # C
icpc program.cpp -o program   # C++
ifort program.f90 -o program  # Fortran
```

### Programming Languages

#### Python

**Available versions**: Multiple Python versions

```bash
# Check available versions
module avail python

# Load Python
module load python/3.11.11
module load python/3.12.2

# Verify
python --version
python3 --version
```

**Installing packages**:
```bash
# User installation
pip install --user package_name

# Or use virtual environments
python -m venv myenv
source myenv/bin/activate
pip install package_name
```

See [Python Optimization Guide](../advanced/python-optimization.md) and [Miniconda Guide](../advanced/miniconda.md).

#### R

**Statistical computing and graphics**:

```bash
# Load R
module load R/4.5.0

# Launch R
R

# Install packages in R
install.packages("package_name")
```

#### Julia

**High-performance numerical computing**:

```bash
module load julia/1.11.3

julia --version
```

#### MATLAB

**Commercial mathematical computing environment**:

```bash
# Check available versions
module avail matlab

# Load MATLAB
module load matlab/r2024b

# GUI (requires X11)
matlab

# Command line
matlab -nodisplay -nosplash

# Run script
matlab -nodisplay -nosplash -r "run('script.m'); exit;"
```

#### Ansys

**Simulation software (Fluent, Lumerical, and more)**:

```bash
module load ansys/2025R1

# Ansys Fluent (CLI)
fluent 2d -g -i sample.jou

# Ansys Fluent (GUI, requires X11)
fluent
```

See the [GUI Programs Guide](../gui-and-tools/gui-programs.md) for running Fluent interactively.

### Parallel Computing

#### MPI (Message Passing Interface)

**OpenMPI**:
```bash
module load openmpi5

# Compile
mpicc program.c -o program
mpicxx program.cpp -o program
mpifort program.f90 -o program

# Run
mpirun -np 4 ./program
```

**MPICH**:
```bash
module load mpich/4.0
```


#### OpenMP

Thread-based parallelism (built into compilers):

```bash
module load gnu14

# Compile with OpenMP
gcc -fopenmp program.c -o program
```

### GPU Computing

#### CUDA

**NVIDIA GPU programming**:

```bash
# Check available versions
module avail cuda

# Load CUDA
module load cuda/11.8
module load cuda/12.4

# Compile
nvcc program.cu -o program

# Verify
nvidia-smi
```

#### Deep Learning Frameworks

**TensorFlow**:
```bash
module load python/3.11.11
module load cuda/12.4

pip install --user tensorflow
```

**PyTorch**:
```bash
module load python/3.11.11
module load cuda/12.4

pip install --user torch torchvision
```

### Scientific Applications

#### Computational Chemistry / Molecular Dynamics

**Gaussian** (quantum chemistry):
```bash
module load gaussian
```

**GROMACS** (molecular dynamics):
```bash
module load gromacs
```

**AMBER** (molecular dynamics):
```bash
module load amber
```

**NAMD** (molecular dynamics):
```bash
module load namd
```

**VASP** (electronic structure, DFT):
```bash
module load vasp
```

**ORCA** (quantum chemistry):
```bash
module load orca
```

**QChem** (quantum chemistry):
```bash
module load qchem
```

#### AI / Inference

**Ollama** (run large language models locally on GPU):
```bash
module load ollama
```

### Libraries

#### Mathematical Libraries

**BLAS/LAPACK**:
```bash
# Provided by OpenBLAS
module load openblas
```

**FFTW** (Fast Fourier Transform):
```bash
module load fftw
```

#### HDF5

**Hierarchical data format**:
```bash
module load hdf5
```

#### NetCDF

**Network Common Data Form**:
```bash
module load netcdf
```

### Development Tools

#### Version Control

**Git** (usually pre-installed):
```bash
git --version

# If not available
module load git
```

#### Build Systems

**Make** (pre-installed):
```bash
make --version
```

#### Debuggers

**Valgrind**:
```bash
module load valgrind
valgrind ./program
```

## Compiler Optimization Flags

### GCC Optimization Levels

```bash
# No optimization
gcc program.c -o program

# Basic optimization
gcc -O1 program.c -o program

# Recommended optimization
gcc -O2 program.c -o program

# Aggressive optimization
gcc -O3 program.c -o program

# Size optimization
gcc -Os program.c -o program
```

### Additional Optimization Flags

```bash
# Architecture-specific
gcc -O3 -march=native program.c -o program

# Enable vectorization reports
gcc -O3 -fopt-info-vec program.c -o program

# OpenMP parallel
gcc -O3 -fopenmp program.c -o program

# Link math library
gcc -O3 program.c -o program -lm
```

### Intel Compiler Optimization

```bash
# Intel specific optimizations
icc -O3 -xHost program.c -o program

# Interprocedural optimization
icc -O3 -ipo program.c -o program

# Profile-guided optimization
icc -O3 -prof-gen program.c -o program
./program
icc -O3 -prof-use program.c -o program
```

## Installing Your Own Software

### Python Packages

**User installation**:
```bash
pip install --user package_name
```

**Virtual environments**:
```bash
python -m venv ~/myenv
source ~/myenv/bin/activate
pip install package_name
```

**Conda/Mamba**:
See [Miniconda Guide](../advanced/miniconda.md)

### R Packages

**User library**:
```R
# In R
install.packages("package_name")

# Or specify location
install.packages("package_name", lib="~/R/library")
```

### Compiling from Source

**General pattern**:
```bash
# Create software directory
mkdir -p ~/software
cd ~/software

# Download source
wget https://example.com/software.tar.gz
tar xzf software.tar.gz
cd software

# Configure
./configure --prefix=$HOME/software/installed

# Compile
make -j 4

# Install
make install

# Add to PATH
echo 'export PATH=$HOME/software/installed/bin:$PATH' >> ~/.bashrc
```

### Using Containers

For software that's difficult to install:

See [Containers Guide](../advanced/containers.md)

## Requesting New Software

### Before Requesting

1. **Check if available**: `module avail software_name`

2. **Try user installation**: Many packages can be installed locally

3. **Check containers**: Software might be available as container

### How to Request

**Open a support ticket**:

1. Go to [HPC Services page](https://hpc.utdallas.edu/services)
2. Click on "Software Installation"
3. Provide:
   - Software name and version
   - Official website/documentation URL
   - Brief description of use case
   - License information (if applicable)
   - Whether others would benefit
   - Required dependencies
   - Timeline/urgency

**Example request**:
```
Software: TensorFlow
Version: 2.14
URL: https://www.tensorflow.org/

Purpose: Deep learning research for image classification

License: Open source (Apache 2.0)

Dependencies: Python 3.9+, CUDA 11.8, cuDNN 8.6

Multiple users in our research group would benefit.

Needed by: [date]
```

### What Gets Installed

**Typically installed system-wide**:

- Popular software with multiple users
- Licensed software with site license
- Software requiring root access
- Complex dependencies

**Better as user install**:

- Python/R packages
- Software with simple installation
- Frequently updated software
- Personal use only

## Software Modules vs User Installation

### When to Use Modules

✓ Large scientific applications  
✓ Compilers and MPI  
✓ Licensed software  
✓ GPU-enabled software  
✓ Multiple version needs  

### When to Install Yourself

✓ Python/R packages  
✓ Quick tools and scripts  
✓ Experimental software  
✓ Frequently updated packages  
✓ Personal utilities  

## Checking Software Versions

### Module Versions

```bash
# See available versions
module avail software_name

# Check loaded version
module list

# After loading
python --version
gcc --version
```

### Command Versions

```bash
# Most software supports --version
command --version

# Or -v
command -v

# Or version subcommand
command version
```

## Performance Considerations

### Choosing Compilers

**GNU**: 

- Free, widely compatible
- Good general-purpose performance
- Best for portability

**Intel**:

- Optimized for Intel processors
- May offer better performance on Juno
- Commercial (but available on cluster)

### MPI Implementations

**OpenMPI**: 

- Most common, good compatibility
- Active development

**Intel MPI**: 

- Optimized for Intel architecture
- Good for large-scale jobs

**MPICH**: 

- Reference implementation
- Lightweight

### Library Choices

**OpenBLAS**:

- Open source alternative
- Good performance

## Common Software Combinations

### Python Data Science

```bash
module purge
module load python/3.11
module load gnu14

pip install --user numpy scipy pandas matplotlib seaborn scikit-learn
```

### GPU Deep Learning

```bash
module purge
module load python/3.11
module load cuda/12.4

pip install --user torch torchvision tensorflow
```

### MPI Applications

```bash
module purge
module load gnu14
module load openmpi/4.1
module load hdf5
```

### MATLAB with Parallel Computing

```bash
module purge
module load matlab/r2024b
```

## Troubleshooting

### Software Not Found After Loading Module

```bash
# Verify module loaded
module list

# Check if command in PATH
which command_name

# Reload module
module unload software
module load software/version
```

### Library Linking Errors

```bash
# Check LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH

# May need additional module
module load dependency

# Check what module provides
module show software_name
```

### Version Conflicts

```bash
# Start fresh
module purge

# Load in order: compiler -> MPI -> libraries -> application
module load gnu14
module load openmpi5
module load application
```

## Quick Reference

### Essential Commands

```bash
# Find software
module avail | grep -i name

# Load software
module load software/version

# Check what's loaded
module list

# Get info
module show software/version

# Unload
module unload software
```

### Common Modules

```bash
# Compilers (gnu12 is loaded by default)
module load gnu14
module load intel/2025.0

# Languages
module load python/3.11
module load R/4.5.0
module load julia/1.11.3

# Applications
module load matlab/r2024b
module load gaussian
module load ansys/2025R1
module load stata

# MPI (openmpi4 is loaded by default)
module load openmpi5

# GPU
module load cuda/12.4
module load cuda/12.6
```

## Next Steps

- [Learn module system details →](modules.md)
- [Submit computational jobs →](../running-programs/slurm.md)
- [Optimize Python workflows →](../advanced/python-optimization.md)
- [Use containers for complex software →](../advanced/containers.md)

## Need Help?

- **Software questions**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Installation requests**: Open ticket → Software Installation
- **Compilation help**: Request consultation via support ticket