# Module System

## What is the Module System?

The module system on Juno provides a way to dynamically load and unload software packages and their dependencies. Instead of having all software available all the time (which would cause conflicts), modules let you selectively enable the software you need.

## Why Use Modules?

### Benefits

**Version management**: Multiple versions of the same software can coexist
```bash
module load python/3.11.11
module load python/3.12.2
```

**Dependency handling**: Automatically loads required dependencies

**Clean environment**: Load only what you need, avoid conflicts

**Easy switching**: Change software versions without reinstalling

## Default Modules on Juno

When you first log in, the following modules are loaded automatically:

```bash
$ module list
Currently Loaded Modules:
  1) autotools        3) gnu12/12.4.0     5) ucx/1.15.0       7) openmpi4/4.1.6
  2) prun/2.2         4) hwloc/2.7.2      6) libfabric/1.19.0  8) ohpc
```

This means **GNU 12** (`gcc`, `g++`, `gfortran`) and **OpenMPI 4** (`mpicc`, `mpif90`) are available immediately after login without any extra `module load` commands. Other versions (e.g., `gnu14`, `openmpi5`) must be loaded explicitly.

## Basic Module Commands

### List Available Modules

```bash
# Show all available modules
module avail

# Search for specific software
module avail python
module avail gnu14
```

### Load a Module

```bash
# Load default version
module load python

# Load specific version
module load python/3.11.11

# Load multiple modules
module load python/3.11.11 gnu14
```

### List Loaded Modules

```bash
# Show currently loaded modules
module list
```

### Unload a Module

```bash
# Unload specific module
module unload python

# Unload all modules
module purge
```

### Get Module Information

```bash
# Show what a module does
module show python/3.11.11

# Display help for module
module help python/3.11.11
```

### Switch Module Versions

```bash
# Switch to different version
module swap python/3.11.11 python/3.12.2

# Or unload old, load new
module unload python/3.11.11
module load python/3.12.2
```

## Common Usage Patterns

### Interactive Use

```bash
# Log in to Juno
ssh netID@juno.utdallas.edu

# Load needed software
module load python/3.11.11

# Use the software
python --version
python my_script.py

# When done, unload or just log out
module unload python
```

### In Job Scripts

**Best practice**: Load modules in job scripts, not in .bashrc

```bash
#!/bin/bash
#SBATCH -J my_job
#SBATCH -o output_%j.log
#SBATCH -p normal
#SBATCH -N 1
#SBATCH -c 4
#SBATCH --mem=8GB
#SBATCH -t 2:00:00

# Load required modules
module purge                    # Start clean
module load python/3.11.11
module load gnu14
module load openmpi5

# Verify loaded modules
module list

# Run your program
python analyze.py
```

### Interactive Session on Compute Node

```bash
# Request resources
salloc -p normal --mem=8GB -c 4

# Start interactive session
srun --pty bash

# Load modules
module load matlab

# Use software
matlab

# Exit when done
exit
```

## Module Organization

### Module Hierarchies

Some module systems use hierarchies where loading a compiler unlocks additional software:

```bash
# Load compiler first
module load gnu14

# Now MPI modules appear
module avail openmpi5

# Load MPI
module load openmpi5

# Now MPI-dependent software appears
module avail netcdf
```

### Module Collections

Save frequently used module combinations:

```bash
# Load your typical modules
module load python/3.11.11 gnu14 openmpi5

# Save as collection
module save mycollection

# Restore collection later
module restore mycollection

# List saved collections
module savelist

# Show collection contents
module describe mycollection
```

## Common Software Modules

### Compilers

```bash
# GCC compiler suite
module load gnu14
module load gnu13

# Intel compiler
module load intel/2025.0

```

### Programming Languages

```bash
# Python
module load python/3.11.11
module load python/3.12.2

# R
module load R/4.5.0

# Julia
module load julia/1.11.3

# Java
module load java/11
```

### Scientific Software

```bash
# MATLAB
module load matlab/r2024b

# Gaussian 16
module load gaussian/16

# Jupyter
module load jupyter
```

### Libraries and Tools

```bash
# MPI implementations
module load openmpi5
module load mpich

# CUDA for GPU
module load cuda/12.4
module load cuda/12.6

```

## Troubleshooting Modules

### Module Not Found

**Problem**: `module load package` returns "not found"

**Solutions**:
```bash
# Check spelling and availability
module avail package

# Check for different versions
module avail | grep -i package

# Software might not be installed
# Contact support to request installation
```

### Version Conflicts

**Problem**: "Module X conflicts with Y"

**Solution**:
```bash
# Unload conflicting module first
module unload X
module load Y

# Or swap directly
module swap X Y

# Or start fresh
module purge
module load Y
```

### Missing Dependencies

**Problem**: Program complains about missing libraries

**Solution**:
```bash
# Check what module loads
module show package_name

# May need to load dependencies manually
module load dependency_module
module load package_name
```

### Changes Not Taking Effect

**Problem**: Module loaded but command not found

**Solution**:
```bash
# Verify module actually loaded
module list

# Check command location
which command_name

# Reload module
module unload package
module load package

# Check PATH
echo $PATH
```

## Advanced Module Usage

### Custom Module Path

Add your own modules:

```bash
# Add custom module path
module use /path/to/my/modules

# Remove custom path
module unuse /path/to/my/modules
```

### Environment Variables

Modules modify environment variables:

```bash
# Before loading
echo $PATH
echo $LD_LIBRARY_PATH

# Load module
module load python/3.11.11

# After loading (paths modified)
echo $PATH
echo $LD_LIBRARY_PATH

# See what module changes
module show python/3.11.11
```

### Checking Module Changes

```bash
# See what module will do before loading
module show python/3.11.11

# Shows:
# - Paths added
# - Environment variables set
# - Dependencies loaded
```

## Best Practices

### 1. Always Specify Versions in Job Scripts

**Bad**:
```bash
module load python    # Might change unexpectedly
```

**Good**:
```bash
module load python/3.11.11    # Explicit version
```

### 2. Start with Clean Environment

```bash
#!/bin/bash
#SBATCH -J my_job

# Purge first to avoid conflicts
module purge

# Load exactly what you need
module load python/3.11.11
module load gnu14
```

### 3. Document Required Modules

In your README or script headers:
```bash
#!/bin/bash
# Required modules:
# - python/3.11.11
# - gnu14
# - openmpi5

module purge
module load python/3.11.11 gnu14 openmpi5
```

### 4. Don't Load Modules in .bashrc

**Why**: Can cause conflicts and unexpected behavior in jobs

**Instead**: Load modules when needed or in job scripts

### 5. Test Module Combinations

```bash
# Test interactively first
module purge
module load package1/version1
module load package2/version2

# Run quick test
python -c "import package; print(package.__version__)"

# If works, add to job script
```

## Module Cheat Sheet

### Essential Commands

```bash
module avail               # List all available modules
module avail python        # Search for Python modules
module load python/3.11.11 # Load specific version
module list                # Show loaded modules
module unload python       # Unload module
module purge               # Unload all modules
module show python/3.11.11 # Show module details
module swap old new        # Replace module
```

### Quick Workflow

```bash
# 1. Find software
module avail | grep package_name

# 2. Load it
module load package_name/version

# 3. Verify
module list
which command_name

# 4. Use it
command_name --version
```

## Example Workflows

### Python Data Science

```bash
module purge
module load python/3.11.11
module load gnu14

# Python packages
python -m pip install --user numpy pandas matplotlib
```

### Compiled Code

```bash
module purge
module load gnu14
module load openmpi5

# Compile
mpicc myprogram.c -o myprogram

# Run
mpirun -np 4 ./myprogram
```

### MATLAB

```bash
module purge
module load matlab/r2024b

# Run MATLAB
matlab -nodisplay -nosplash -r "run('script.m'); exit;"
```

### GPU Computing

```bash
module purge
module load cuda/12.4

# Compile CUDA code
nvcc mycode.cu -o mycode

# Run
./mycode
```

## Module Management for Groups

### Shared Modules

For research groups:

```bash
# Group can maintain shared modules in project space
module use /groups/groupname/modules

# Load group-specific software
module load custom_software/1.0
```

### Requesting New Software

When software you need isn't available:

1. **Check if it exists**: `module avail | grep -i software_name`

2. **Try installing locally** (user space):
   - Python: `pip install --user package`
   - Conda: Create environment
   - From source: Install to `$HOME/software`

3. **Request installation**:
   - Open ticket at HPC Services page
   - Provide: software name, version, URL, purpose
   - Indicate if others would benefit

4. **Use containers** (Singularity/Apptainer):
   - See [Containers Guide](../advanced/containers.md)

## Software Management Alternatives

### When NOT to Use Modules

**Use alternative methods for**:

**Python packages**: Use conda environments or pip
```bash
pip install --user package_name
```

**R packages**: Install in personal library
```R
install.packages("package_name")
```

**Conda/Mamba**: Full environment management
```bash
conda create -n myenv python=3.11
conda activate myenv
```

See:

- [Python Optimization Guide](../advanced/python-optimization.md)
- [Miniconda Guide](../advanced/miniconda.md)

## Checking Module Availability

### Search Strategies

```bash
# Case-insensitive search
module avail -i matlab

# List all and grep
module avail 2>&1 | grep -i tensorflow

# Show module tree
module avail -t
```

### Verify Versions

```bash
# Load and check
module load python/3.11
python --version

# Check library versions
python -c "import numpy; print(numpy.__version__)"
```

## Common Issues and Solutions

### Issue: Module Command Not Found

```bash
# Module system not initialized
# Usually automatic, but if needed:
source /etc/profile.d/modules.sh
```

### Issue: Software Doesn't Run After Loading

```bash
# Verify module loaded
module list

# Check path
which python

# Try reloading
module unload python
module load python/3.11
```

### Issue: Need Multiple Conflicting Versions

```bash
# Use separate sessions/jobs
# Job 1:
module load python/3.11

# Job 2 (different job):
module load python/3.12
```

## Next Steps

- [Explore available software →](software.md)
- [Learn to submit jobs →](../running-programs/slurm.md)
- [Set up Python environments →](../advanced/miniconda.md)

## Need Help?

- **Module questions**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Software requests**: Open ticket for Software Installation
- **Module errors**: Include error message and `module list` output in ticket