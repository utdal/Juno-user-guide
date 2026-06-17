# Virtual Environments with Miniconda

## Overview

Miniconda is a lightweight version of Anaconda that provides conda package management and Python environments. It's ideal for creating isolated environments with specific package versions on HPC clusters. This page covers loading Miniconda on Juno, creating and managing environments, using them inside SLURM jobs, sharing environments with your research group, and keeping their storage footprint under control.

## Why Use Conda on HPC?

### Benefits

✓ **Isolated environments**: Separate packages per project  
✓ **Version control**: Pin exact package versions  
✓ **Reproducibility**: Share environment specifications  
✓ **Easy installation**: No root access needed  
✓ **Binary packages**: Pre-compiled, fast installation  
✓ **Cross-language**: Python, R, C++, and more  

### Conda vs pip

| Feature | conda | pip |
|---------|-------|-----|
| **Languages** | Multi-language | Python only |
| **Dependencies** | Handles system libs | Python packages only |
| **Binaries** | Pre-compiled | Sometimes builds from source |
| **Environments** | Full isolation | Needs virtual env |
| **Speed** | Slower solving | Faster install |

**Best practice**: Use conda for environments, pip for packages when needed

## Loading Miniconda

### Load

```bash
[netID@juno-l-01 ~]$ module load miniconda
```

### Initialize Shell (One Time Only)

```bash
# Initialize conda for bash
[netID@juno-l-01 ~]$ conda init bash

# Reload shell configuration
[netID@juno-l-01 ~]$ source ~/.bashrc

# An initialized shell looks like this
(base) [netID@juno-l-01 ~]$

# Verify installation
(base) [netID@juno-l-01 ~]$ conda --version
```

### Configure Conda

```bash
# Disable auto-activation of base environment
conda config --set auto_activate_base false

# Set channel priority
conda config --set channel_priority strict

# Add conda-forge channel (recommended)
conda config --add channels conda-forge

# View configuration
conda config --show
```

## Creating Environments

### Basic Environment

```bash
# Create environment with Python version
conda create -p /path/to/myenv python=3.9

# Create with specific packages
conda create -p /path/to/myenv python=3.9 numpy pandas matplotlib

# Create from specification
conda create -p /path/to/myenv python=3.9 --file requirements.txt
```

!!! note
    It's recommended that you create a conda environment in `~/work` or `/groups/` directory, as the installation can easily overflow your home directory.

### Activate/Deactivate

```bash
# Activate environment
conda activate /path/to/myenv

# Check active environment
conda info --envs

# Deactivate
conda deactivate
```

### List Environments

```bash
# List all environments
conda env list

# Or
conda info --envs
```

## Managing Packages

### Installing Packages

```bash
# Activate environment first
conda activate /path/to/myenv

# Install single package
conda install numpy

# Install specific version
conda install numpy=1.24.0

# Install multiple packages
conda install numpy pandas matplotlib scikit-learn

# Install from conda-forge
conda install -c conda-forge package_name

# Use pip if package not in conda
pip install package_name
```

### Listing Packages

```bash
# List packages in active environment
conda list

# List packages in specific environment
conda list -p /path/to/myenv

# Search for package
conda search numpy
```

### Updating Packages

```bash
# Update specific package
conda update numpy

# Update all packages
conda update --all

# Update conda itself
conda update conda
```

### Removing Packages

```bash
# Remove package
conda remove numpy

# Remove multiple packages
conda remove numpy pandas
```

## Environment Management

### Export Environment

```bash
# Export to YAML file (recommended)
conda env export > environment.yml

# Export without builds (more portable)
conda env export --no-builds > environment.yml

# Export from history (minimal, reproducible)
conda env export --from-history > environment.yml
```

**Example environment.yml**:
```yaml
name: /path/to/myenv
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - numpy=1.24
  - pandas=2.0
  - matplotlib=3.7
  - scikit-learn=1.3
  - pip
  - pip:
      - custom-package==1.0.0
```

### Create from YAML

```bash
# Create environment from file
conda env create -f environment.yml

# Update existing environment
conda env update -f environment.yml --prune
```

### Clone Environment

```bash
# Clone existing environment
conda create -p /path/to/newenv --clone /path/to/oldenv
```

### Remove Environment

```bash
# Remove environment
conda env remove -p /path/to/myenv

# Or
conda remove -p /path/to/myenv --all
```

## Sharing Environments with Your Research Group

There are two ways to share a conda environment with others in your group. Sharing a
**recipe** (`environment.yml`) is the portable, reproducible default; sharing a **single
installed environment** in group storage saves disk space and guarantees everyone runs
the exact same build.

### Option 1: Share an environment.yml file (recommended)

Each person creates their own copy of the environment from a shared recipe file. This is
portable across clusters and keeps each user's environment independent.

```bash
# 1. You: export the recipe (use --from-history for a minimal, portable file)
conda env export --from-history > environment.yml

# 2. Put it where the group can read it — group storage or a shared git repo
cp environment.yml /groups/<pi-name>/envs/myproject-environment.yml

# 3. A colleague: recreate the environment under their own account
conda env create -f /groups/<pi-name>/envs/myproject-environment.yml
```

Keeping `environment.yml` in your project's git repository is the most reproducible
approach — anyone who clones the repo can recreate the environment with one command.

### Option 2: Share one installed environment in group storage

Install the environment **once** in `/groups/<pi-name>` and have everyone activate it by
full path. This avoids each member installing (and storing) their own copy.

```bash
# You: create the environment in shared group storage, not your home directory
conda create -p /groups/<pi-name>/envs/shared-rnaseq python=3.11
conda activate /groups/<pi-name>/envs/shared-rnaseq
conda install -c conda-forge numpy pandas scipy

# Anyone in the group: activate it by full path (no install needed)
module load miniconda      # if not already loaded
conda activate /groups/<pi-name>/envs/shared-rnaseq
```

In a job script, reference it the same way:

```bash
module load miniconda
conda activate /groups/<pi-name>/envs/shared-rnaseq
python analysis.py
```

!!! note "Permissions for shared environments"
    For others to activate a shared environment, they need read and execute access to
    its files. Group storage under `/groups/<pi-name>` is shared with your group by
    default, but if colleagues hit "permission denied," fix the group permissions:

    ```bash
    # Make the environment readable and traversable by the group
    chmod -R g+rX /groups/<pi-name>/envs/shared-rnaseq
    ```

    Treat shared environments as read-only for members other than the owner — if one
    person `conda install`s into it, the change affects everyone. Designate one
    maintainer for updates, or have each member use Option 1 instead. See
    [Storage and Data Transfer](../getting-started/storage.md) for more on group access.

## Using Conda in Jobs

### Basic Job Script

```bash
#!/bin/bash
#SBATCH -J conda_job
#SBATCH -o output_%j.log
#SBATCH -p normal
#SBATCH -c 4
#SBATCH --mem=16GB
#SBATCH -t 2:00:00

# Load conda
module load miniconda

# Activate environment (use the full path)
conda activate /path/to/myenv

# Run Python script
python script.py

# Deactivate (optional, job ends anyway)
conda deactivate
```

### Multiple Environments

```bash
#!/bin/bash
#SBATCH -J multi_env_job

module load miniconda

# Preprocessing with one environment
conda activate /path/to/preprocess_env
python preprocess.py

# Analysis with another environment
conda activate /path/to/analysis_env
python analyze.py

# Plotting with third environment
conda activate /path/to/viz_env
python plot.py
```

## Practical Examples

### Example 1: Data Science Environment

```bash
# Create environment
conda create -p /path/to/datascience python=3.9

# Activate
conda activate /path/to/datascience

# Install packages
conda install numpy pandas matplotlib seaborn scikit-learn jupyter

# Install deep learning (optional)
conda install pytorch torchvision -c pytorch

# Install additional tools
pip install plotly

# Export for reproducibility
conda env export --from-history > datascience.yml
```

### Example 2: Bioinformatics Pipeline

```bash
# Create environment
conda create -p /path/to/bioinfo python=3.9

# Activate
conda activate /path/to/bioinfo

# Install bioinformatics tools
conda install -c bioconda biopython blast bowtie2 samtools

# Install Python packages
conda install pandas numpy matplotlib

# Export
conda env export > bioinfo.yml
```

### Example 3: Machine Learning with GPU

```bash
# Create environment
conda create -p /path/to/ml_gpu python=3.9

# Activate
conda activate /path/to/ml_gpu

# Install PyTorch with CUDA
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Or TensorFlow
conda install tensorflow-gpu

# Install other ML tools
conda install scikit-learn pandas numpy matplotlib

# Export
conda env export --from-history > ml_gpu.yml
```

**Job script**:
```bash
#!/bin/bash
#SBATCH -J ml_training
#SBATCH -p h100
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32GB
#SBATCH -t 8:00:00

module load miniconda
conda activate /path/to/ml_gpu

python train_model.py
```

## Storage Management

### Check Environment Sizes

```bash
# Check size of all environments
du -sh $(conda info --base)/envs/*

# Check specific environment
du -sh $(conda info --base)/envs/myenv
```

### Clean Up

```bash
# Remove unused packages and caches
conda clean --all

# Remove specific cache
conda clean --packages
conda clean --tarballs

# Remove index cache
conda clean --index-cache
```

### Use Scratch for Large Environments

```bash
# Create environments in scratch
conda create -p ~/scratch/envs/myenv python=3.9

# Activate with full path
conda activate ~/scratch/envs/myenv

# Or set envs directory
conda config --add envs_dirs ~/scratch/envs
```

## Best Practices

### 1. Environment Per Project

```bash
# Project structure
~/projects/
├── project1/
│   ├── environment.yml
│   └── code/
├── project2/
│   ├── environment.yml
│   └── code/
```

### 2. Use environment.yml Files

```yaml
# environment.yml
name: myproject
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy>=1.24
  - pandas>=2.0
  - pip:
      - custom-package==1.0
```

### 3. Minimal Environments

```bash
# Only install what you need
conda create -n minimal python=3.9 numpy pandas

# Not everything from base
```

### 4. Version Control

```bash
# Add to git repository
git add environment.yml
git commit -m "Add environment specification"

# .gitignore should exclude:
# miniconda3/
# .conda/
# *.pyc
# __pycache__/
```

### 5. Document Dependencies

```bash
# Create requirements.txt for pip packages
pip freeze > requirements.txt

# Or use conda
conda list --export > package-list.txt
```

## Troubleshooting

### Conda Command Not Found

**Problem**: `conda: command not found`

**Solution**:
```bash
# Load and initialize conda
module load miniconda
source ~/.bashrc

# Or re-run init
conda init bash
source ~/.bashrc
```

### Slow Environment Solving

**Problem**: Creating environment takes very long

**Solutions**:
```bash
# Use mamba (faster conda)
conda install -n base -c conda-forge mamba

# Use mamba instead of conda
mamba create -n myenv python=3.9 numpy pandas

# Use specific channels
conda create -n myenv -c conda-forge python=3.9
```

### Conflicts During Install

**Problem**: "Solving environment: failed with initial frozen solve"

**Solutions**:
```bash
# Update conda
conda update conda

# Try installing one package at a time
conda create -p /path/to/myenv python=3.9
conda activate /path/to/myenv
conda install numpy
conda install pandas

# Use pip for problematic packages
pip install problematic-package
```

### Out of Disk Space

**Problem**: Home directory quota exceeded

**Solutions**:
```bash

# Set package cache location
conda config --add pkgs_dirs ~/scratch/conda_pkgs

# Clean up
conda clean --all
```

### Environment Not Activating in Job

**Problem**: Environment doesn't activate in SLURM job

**Solution**:
```bash
#!/bin/bash
#SBATCH -J test

# Must load miniconda first
module load miniconda

# Then activate
conda activate /path/to/myenv

python script.py
```

## Advanced Usage

### Using Mamba

**Mamba is a faster alternative to conda**:

```bash
# Install mamba
conda install -n base -c conda-forge mamba

# Use mamba like conda
mamba create -n myenv python=3.9
mamba install numpy pandas
mamba update --all
```

### Environment Variables

```bash
# Set environment variables in environment
conda env config vars set MY_VAR=value -n myenv

# View variables
conda env config vars list -n myenv

# Use in scripts
conda activate myenv
echo $MY_VAR
```

### Custom Channels

```bash
# Add institutional channel
conda config --add channels https://conda.institution.edu/

# Install from specific channel
conda install -c my-channel package_name
```


## Conda vs Alternatives

### When to Use Conda

✓ Complex dependencies (C libraries, etc.)  
✓ Multi-language projects  
✓ Need specific versions  
✓ Binary compatibility important  

### When to Use virtualenv + pip

✓ Simple Python-only project  
✓ Want lightweight solution  
✓ All packages on PyPI  

### When to Use Containers

✓ Need system-level isolation  
✓ Sharing with others  
✓ Complex system dependencies  

See [Containers Guide](containers.md)

## Example Workflows

### Workflow 1: Quick Analysis

```bash
# Create environment
conda create -p /path/to/analysis python=3.9 pandas numpy matplotlib jupyter

# Start Jupyter
conda activate /path/to/analysis
jupyter notebook
```

### Workflow 2: Reproducible Research

```bash
# Initial setup
conda create -p /path/to/research python=3.9
conda activate /path/to/research
conda install numpy scipy pandas matplotlib scikit-learn

# Work on project
python analysis.py

# Export when done
conda env export --from-history > environment.yml

# Others can recreate
conda env create -f environment.yml
```

### Workflow 3: Multiple Projects

```bash
# Project 1: TensorFlow 2.x
conda create -p /path/to/tf2 python=3.9 tensorflow pandas
conda activate /path/to/tf2
python train_tf2.py
conda deactivate

# Project 2: PyTorch
conda create -p /path/to/pytorch python=3.9 pytorch torchvision -c pytorch
conda activate /path/to/pytorch
python train_pytorch.py
conda deactivate
```

## Quick Reference

### Essential Commands

```bash
# Create environment
conda create -p /path/to/myenv python=3.9

# Activate
conda activate /path/to/myenv

# Install packages
conda install numpy pandas

# List environments
conda env list

# Export
conda env export > environment.yml

# Create from file
conda env create -f environment.yml

# Remove environment
conda env remove -p /path/to/myenv

# Clean up
conda clean --all
```

### Common Package Combinations

```bash
# Data science
conda install numpy pandas matplotlib seaborn scikit-learn jupyter

# Machine learning
conda install pytorch torchvision -c pytorch
# or
conda install tensorflow

# Bioinformatics
conda install -c bioconda biopython blast bowtie2

# Web scraping
conda install requests beautifulsoup4 selenium

# Visualization
conda install matplotlib seaborn plotly bokeh
```

## Next Steps

- [Optimize Python performance →](python-optimization.md)
- [Use containers as alternative →](containers.md)
- [Learn about parallelism →](../running-programs/parallelism.md)

## Need Help?

- **Conda issues**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Environment problems**: Include `conda list` output in ticket
- **Package requests**: Check if available via conda before requesting system installation
