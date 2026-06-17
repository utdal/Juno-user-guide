# Containers on Juno

## Overview

Containers are lightweight, portable software packages that include an application and all its dependencies, giving you a consistent environment across different systems. On Juno, containers run with **Apptainer** (formerly Singularity). This page covers why and when to use containers on HPC, building or pulling images, binding directories, GPU support, running containers inside SLURM jobs, and converting Docker images to Apptainer.

## Why Use Containers on HPC?

### Benefits

✓ **Reproducibility**: Same environment everywhere  
✓ **Portability**: Works on laptop, cluster, cloud  
✓ **Dependency management**: All libraries bundled together  
✓ **Version control**: Pin exact software versions  
✓ **Isolation**: No conflicts with system software  
✓ **Easy deployment**: Pull pre-built containers  

### Use Cases

- **Complex dependencies**: Software with difficult installation
- **Reproducible research**: Ensure exact environment
- **Software not available**: Use containers from Docker Hub
- **Legacy software**: Run old software versions
- **Python/R environments**: Alternative to conda
- **Standardized pipelines**: Bioinformatics, ML workflows

## Apptainer (Singularity)

On HPC systems, we use **Apptainer** (previously called **Singularity**) instead of Docker to run containers. Apptainer can convert a Docker container into an Apptainer container, and the Apptainer container's binary can be run like a regular Linux command. This makes it easy to run Apptainer containers inside user batch jobs or interactive shells like regular software.

```
  ┌──────────────────────┐        ┌──────────────┐        ┌──────────────────────┐
  │  1. Build / Pull     │        │  2. Transfer │        │  3. Run on Juno      │
  │  (local or cloud)    │        │              │        │                      │
  │                      │        │              │        │  $ sbatch job.sh     │
  │  apptainer pull      │        │  scp         │        │                      │
  │    docker://…        │──────► │  myapp.sif   │──────► │  apptainer exec \    │
  │                      │        │  netID@juno… │        │    myapp.sif \       │
  │  sudo apptainer      │        │  :~/scratch/ │        │    script.py         │
  │    build myapp.sif   │        │              │        │                      │
  │    myapp.def         │        │              │        │  (on compute node    │
  │                      │        │              │        │   via SLURM)         │
  └──────────────────────┘        └──────────────┘        └──────────────────────┘
         myapp.sif  ─────────────────────────────────────────►  myapp.sif
        (SIF image)                                           runs in user account
```

### Key Differences from Docker

| Feature | Docker | Singularity |
|---------|--------|-------------|
| **Root access** | Required to run container | Not required, runs in user account |
| **HPC friendly** | No | Yes |
| **Integration** | Isolated | Accesses host filesystem |
| **User identity** | Root inside | Same user |
| **Security** | Privileged | Unprivileged |

## Getting Started

### Check Availability

```bash
# Check if apptainer is available
module avail apptainer

# Load module
module load apptainer/1.3.4

# Verify installation
apptainer --version
```

### Basic Concepts

**Image**: The container template (like a snapshot)  
**Container**: Running instance of an image  
**SIF**: Singularity Image Format (`.sif` file)  

## Building Containers

### From Docker Hub

**Pull pre-built container**:

```bash
# Pull from Docker Hub
apptainer pull docker://ubuntu:22.04

# Creates: ubuntu_22.04.sif

# Pull specific software
apptainer pull docker://tensorflow/tensorflow:latest-gpu

# Pull from other registries
apptainer pull docker://quay.io/biocontainers/blast:2.12.0--pl5262h3289130_0
```

### From Definition File

**Create definition file** (`mycontainer.def`):

```singularity
Bootstrap: docker
From: ubuntu:22.04

%post
    # Install dependencies
    apt-get update
    apt-get install -y python3 python3-pip
    pip3 install numpy pandas scikit-learn

%environment
    export LC_ALL=C
    export PATH=/usr/local/bin:$PATH

%runscript
    python3 "$@"

%labels
    Author netID@utdallas.edu
    Version v1.0

%help
    This container includes Python 3 with scientific libraries.
    Usage: singularity run mycontainer.sif script.py
```

**Build container**:

```bash
# Build on a system where you have sudo (your laptop)
sudo apptainer build mycontainer.sif mycontainer.def

# Then transfer to Juno
scp mycontainer.sif netID@juno.utdallas.edu:~/scratch/
```

!!! note "Building Containers"
    You need root/sudo to build containers. Build on your local machine or use:
    - Singularity Hub (deprecated)
    - GitHub Actions
    - Sylabs Cloud

### From Sandbox (Development)

```bash
# Create writable sandbox (local machine with sudo)
sudo apptainer build --sandbox myapp/ docker://ubuntu:22.04

# Enter and modify
sudo apptainer shell --writable myapp/
# Install software, make changes
exit

# Convert to read-only SIF
sudo apptainer build myapp.sif myapp/
```

## Running Containers

### Interactive Shell

```bash
# Start interactive shell in container
apptainer shell mycontainer.sif

# With GPU support
apptainer shell --nv tensorflow.sif

# Bind additional directories
apptainer shell --bind ~/scratch:/data mycontainer.sif
```

### Execute Commands

```bash
# Run command in container
apptainer exec mycontainer.sif python script.py

# With arguments
apptainer exec mycontainer.sif python script.py --input data.csv

# Run with GPU
apptainer exec --nv pytorch.sif python train.py
```

### Run (Using Runscript)

```bash
# Execute container's runscript
apptainer run mycontainer.sif

# Pass arguments to runscript
apptainer run mycontainer.sif arg1 arg2
```

## Directory Binding

By default, Singularity binds:

- Home directory (`$HOME`)
- Current directory (`$PWD`)
- `/tmp`

### Bind Additional Directories

```bash
# Bind single directory
apptainer exec --bind ~/scratch:/data mycontainer.sif ls /data

# Bind multiple directories
apptainer exec \
  --bind ~/scratch:/scratch \
  --bind /project/groupname:/project \
  mycontainer.sif python process.py

# Bind with read-only
apptainer exec --bind /data:/data:ro mycontainer.sif python read_data.py
```

### Environment Variables

```bash
# Set environment variable
apptainer exec --env MY_VAR=value mycontainer.sif python script.py

# Use environment file
apptainer exec --env-file vars.env mycontainer.sif python script.py
```

## GPU Support

### Using NVIDIA GPUs

```bash
# Enable NVIDIA GPU support
apptainer exec --nv pytorch.sif python train_gpu.py

# Verify GPU access inside container
apptainer exec --nv pytorch.sif nvidia-smi
```

### CUDA Compatibility

Container must have compatible CUDA version:

```bash
# Check host CUDA version
module load cuda/12.4
nvidia-smi

# Use container with matching CUDA
apptainer pull docker://tensorflow/tensorflow:2.14.0-gpu
```

## Using Containers in Jobs

### Basic Job Script

```bash
#!/bin/bash
#SBATCH -J container_job
#SBATCH -o output_%j.log
#SBATCH -p normal
#SBATCH -N 1
#SBATCH -c 4
#SBATCH --mem=16GB
#SBATCH -t 2:00:00

# Load apptainer
module load apptainer/1.3.4

# Run containerized application
apptainer exec ~/scratch/mycontainer.sif \
  python ~/scratch/scripts/process.py
```

### GPU Job with Container

```bash
#!/bin/bash
#SBATCH -J gpu_container
#SBATCH -p a30                  # or h100
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32GB
#SBATCH -t 4:00:00

module load apptainer/1.3.4

# Run with GPU support
apptainer exec --nv \
  --bind ~/scratch:/workspace \
  ~/scratch/tensorflow-gpu.sif \
  python /workspace/train_model.py
```

### MPI with Containers

```bash
#!/bin/bash
#SBATCH -J mpi_container
#SBATCH -N 2
#SBATCH -n 32
#SBATCH -t 2:00:00

module load apptainer/1.3.4
module load openmpi5

# Run MPI application in container
mpirun -np $SLURM_NTASKS \
  apptainer exec mycontainer.sif \
  /app/mpi_program
```

## Common Container Sources

### Docker Hub

```bash
# Official images
apptainer pull docker://python:3.9
apptainer pull docker://ubuntu:22.04
apptainer pull docker://continuumio/miniconda3

# Scientific software
apptainer pull docker://rocker/tidyverse    # R with tidyverse
apptainer pull docker://jupyter/scipy-notebook
```

### BioContainers

```bash
# Bioinformatics tools
apptainer pull docker://quay.io/biocontainers/samtools:1.15
apptainer pull docker://quay.io/biocontainers/blast:2.12.0
apptainer pull docker://quay.io/biocontainers/bowtie2:2.4.5
```

### NVIDIA NGC

```bash
# GPU-optimized containers
apptainer pull docker://nvcr.io/nvidia/tensorflow:22.12-tf2-py3
apptainer pull docker://nvcr.io/nvidia/pytorch:22.12-py3
```

## Practical Examples

### Example 1: TensorFlow with GPU

```bash
#!/bin/bash
#SBATCH -J tf_training
#SBATCH -p h100
#SBATCH --gres=gpu:1
#SBATCH -t 8:00:00

module load apptainer/1.3.4

# Pull TensorFlow container (first time only)
# apptainer pull docker://tensorflow/tensorflow:latest-gpu

# Run training
apptainer exec --nv \
  --bind ~/scratch:/workspace \
  tensorflow_latest-gpu.sif \
  python /workspace/train_model.py \
    --data /workspace/data \
    --output /workspace/models
```

### Example 2: Bioinformatics Pipeline

```bash
#!/bin/bash
#SBATCH -J blast_pipeline
#SBATCH -p normal
#SBATCH -c 8
#SBATCH --mem=32GB
#SBATCH -t 4:00:00

module load apptainer/1.3.4

# Pull BLAST container
BLAST_CONTAINER=~/scratch/containers/blast.sif
if [ ! -f $BLAST_CONTAINER ]; then
    apptainer pull $BLAST_CONTAINER \
      docker://quay.io/biocontainers/blast:2.12.0--pl5262h3289130_0
fi

# Run BLAST
apptainer exec \
  --bind ~/scratch/data:/data \
  $BLAST_CONTAINER \
  blastp -query /data/query.fasta \
         -db /data/database \
         -out /data/results.txt \
         -num_threads $SLURM_CPUS_PER_TASK
```

### Example 3: Custom Python Environment

**Definition file** (`scientific-python.def`):

```apptainer
Bootstrap: docker
From: python:3.9

%post
    pip install --no-cache-dir \
        numpy \
        scipy \
        pandas \
        matplotlib \
        seaborn \
        scikit-learn \
        jupyter

%environment
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8

%runscript
    exec python "$@"
```

**Usage**:
```bash
# Build (on local machine with sudo)
sudo apptainer build scientific-python.sif scientific-python.def

# Transfer to Juno and use
apptainer exec scientific-python.sif python analysis.py
```

### Example 4: RStudio Server

```bash
#!/bin/bash
#SBATCH -J rstudio
#SBATCH -p normal
#SBATCH -c 4
#SBATCH --mem=16GB
#SBATCH -t 4:00:00

module load apptainer/1.3.4

# Pull RStudio container
apptainer pull docker://rocker/rstudio:latest

# Start RStudio Server
apptainer exec \
  --bind ~/scratch:/workspace \
  rstudio_latest.sif \
  rserver --www-address=0.0.0.0 --www-port=8787
```

## Best Practices

### 1. Store Containers Efficiently

```bash
# Create containers directory
mkdir -p ~/scratch/containers

# Store containers there
cd ~/scratch/containers
apptainer pull docker://python:3.9

# Reference in scripts
CONTAINER=~/scratch/containers/python_3.9.sif
```

### 2. Cache Pull Results

```bash
# Set cache directory
export APPTAINER_CACHEDIR=~/scratch/singularity_cache
mkdir -p $APPTAINER_CACHEDIR

# Pull (cached for future pulls)
apptainer pull docker://ubuntu:22.04
```

### 3. Version Control Definition Files

```bash
# Keep definition files in git
git add mycontainer.def
git commit -m "Add container definition"

# Document container versions
# mycontainer.def v1.0
# Date: 2024-01-15
# Purpose: Python 3.9 with ML libraries
```

### 4. Test Locally First

```bash
# Build and test on local machine
sudo apptainer build test.sif test.def
apptainer exec test.sif python test_script.py

# Then transfer to cluster
scp test.sif netID@juno.utdallas.edu:~/scratch
```

### 5. Use Specific Tags

```bash
# Bad: Latest may change
apptainer pull docker://python:latest

# Good: Specific version
apptainer pull docker://python:3.9.18
```

## Troubleshooting

### Permission Denied

**Problem**: Can't write to directory inside container

**Solution**: Ensure bound directories have correct permissions
```bash
# Check permissions
ls -ld ~/scratch

# Make sure you can write
touch ~/scratch/test.txt
```

### Module Not Found (Python)

**Problem**: Python packages not found in container

**Solution**: Packages must be installed in container, not on host
```bash
# Install in container definition file
%post
    pip install numpy pandas
```

### GPU Not Accessible

**Problem**: `nvidia-smi` not working inside container

**Solutions**:
```bash
# Use --nv flag
apptainer exec --nv container.sif nvidia-smi

# Check CUDA module loaded
module load cuda
```

### Container Not Found

**Problem**: `singularity exec: command not found`

**Solution**:
```bash
# Load singularity module
module load apptainer/1.3.4

# Check availability
module avail apptainer
```

### Slow Container Pull

**Problem**: Pulling takes very long

**Solutions**:
```bash
# Pull during interactive session
salloc -p normal -t 1:00:00
apptainer pull docker://large-image:latest

# Or in job script (better)
#!/bin/bash
#SBATCH -t 2:00:00
apptainer pull docker://large-image:latest
```

## Advanced Topics

### Overlay Filesystems

**Create writable overlay**:
```bash
# Create overlay image
apptainer overlay create --size 1024 overlay.img

# Use overlay
apptainer exec --overlay overlay.img container.sif python script.py
```

### Multi-Stage Builds

**Definition file with stages**:
```singularity
Bootstrap: docker
From: golang:1.19 as builder

%post
    # Build stage
    cd /tmp
    git clone https://github.com/example/app.git
    cd app
    go build -o /app

Bootstrap: docker
From: alpine:latest
Stage: final

%files from builder
    /app /usr/local/bin/app

%runscript
    exec /usr/local/bin/app "$@"
```

### Container Inspection

```bash
# Inspect container
apptainer inspect container.sif

# View definition file
apptainer inspect --deffile container.sif

# Check labels
apptainer inspect --labels container.sif

# View runscript
apptainer inspect --runscript container.sif
```

## Container Registries

### Sylabs Cloud

```bash
# Push to cloud (requires account)
apptainer push mycontainer.sif library://username/collection/image:tag

# Pull from cloud
apptainer pull library://username/collection/image:tag
```

### GitHub Container Registry

```bash
# Pull from GitHub
apptainer pull docker://ghcr.io/username/image:tag
```

## Converting Docker to Singularity

```bash
# Most Docker containers work directly
apptainer pull docker://repository/image:tag

# Some Docker features not supported:
# - USER directive (runs as your user anyway)
# - EXPOSE ports (use --net for networking)
# - VOLUME (use --bind instead)
```

## Resource Recommendations

### Container Size

- Keep containers reasonably sized (<5GB ideal)
- Use multi-stage builds to reduce size
- Clean up in `%post` section:
  ```singularity
  %post
      apt-get clean
      rm -rf /var/lib/apt/lists/*
  ```

### Storage Location

```bash
# Store in scratch, not home
~/scratch/containers/

# Link commonly used containers
ln -s ~/scratch/containers/python.sif ~/python.sif
```

## Quick Reference

### Essential Commands

```bash
# Pull container
apptainer pull docker://image:tag

# Run command
apptainer exec container.sif command

# Interactive shell
apptainer shell container.sif

# With GPU
apptainer exec --nv container.sif command

# Bind directory
apptainer exec --bind /path:/mount container.sif command

# Check version
apptainer --version
```

### Common Containers

```bash
# Python
apptainer pull docker://python:3.9

# R/RStudio
apptainer pull docker://rocker/tidyverse

# TensorFlow GPU
apptainer pull docker://tensorflow/tensorflow:latest-gpu

# PyTorch
apptainer pull docker://pytorch/pytorch:latest

# Jupyter
apptainer pull docker://jupyter/scipy-notebook
```

## Next Steps

- [Optimize Python code →](python-optimization.md)
- [Use Miniconda as alternative →](miniconda.md)
- [Learn about parallelism →](../running-programs/parallelism.md)

## Need Help?

- **Container issues**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Building containers**: Request consultation
- **Finding containers**: Ask about specific software needs
