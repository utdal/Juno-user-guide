# Running Common Scientific Programs

This page covers how to run specific scientific programs on Juno — both as batch jobs and interactively.

---

## MATLAB

### Batch Job (Recommended)

```bash
#!/bin/bash
#SBATCH --job-name=matlab_job
#SBATCH --output=matlab_%j.out
#SBATCH --error=matlab_%j.err
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=16G
#SBATCH --time=12:00:00

module load matlab/r2024b

matlab -nodisplay -nosplash -nodesktop -r "run('path/to/your/script.m'); exit;"
```

### Interactive (Command Line)

```bash
# Step 1: Request a compute node
salloc -p normal --mem=2GB

# Step 2: Start interactive session
srun --pty bash

# Step 3: Load and run MATLAB
module load matlab/r2024b
matlab -nodisplay -nosplash -nodesktop -r "run('path/to/your/script.m'); exit;"
```

### Interactive (GUI via X11)

Requires logging in with `ssh -X`. See [GUI Programs](../gui-and-tools/gui-programs.md).

```bash
# Log in with X11 forwarding
ssh -X netID@juno.utdallas.edu

# Request a compute node
salloc -p normal --mem=2GB
squeue --me                   # note which node was assigned, e.g. c-04-01

# SSH into the compute node with X11
ssh -X c-04-01

# Load and launch MATLAB GUI
module load matlab/r2024b
matlab
```

Or use [**Open OnDemand**](../gui-and-tools/open-ondemand.md) → Interactive Apps → MATLAB (easiest option).

---

## Gaussian

### Batch Job

```bash
#!/bin/bash
#SBATCH --job-name=gaussian_job
#SBATCH --output=gaussian_%j.out
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00

module load gaussian/16

g16 input.com > output.log
```

Gaussian automatically uses `~/scratch` for `.rwf` scratch files during batch jobs — you do not need to specify the path.

### Interactive

```bash
salloc -p normal --mem=2G
srun --pty bash

module load gaussian/16
g16 input.com > output.log
```

---

## Ansys Fluent

### Batch Job (CLI)

```bash
#!/bin/bash
#SBATCH --job-name=fluent_job
#SBATCH --output=fluent_%j.out
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=64G
#SBATCH --time=8:00:00

module load ansys/2025R1

fluent 2d -g -i sample.jou
```

Replace `2d` with `3d` for 3D cases. The `-g` flag disables the GUI and `-i` specifies the journal file.

### Interactive (CLI)

```bash
salloc -p normal --mem=2GB
srun --pty bash

module load ansys/2025R1
fluent 2d -g -i sample.jou
```

### Interactive (GUI via X11)

```bash
# Log in with X11 forwarding
ssh -X netID@juno.utdallas.edu

# Request a compute node
salloc -p normal --mem=2GB
squeue --me                   # e.g. c-04-01

# SSH into the compute node with X11
ssh -X c-04-01

# Load and launch Fluent GUI
module load ansys/2025R1
fluent
```

---

## Python

Python is an interpreted language and typically needs environment management. See:

- [Virtual Environments with Miniconda](../advanced/miniconda.md) — recommended for managing packages
- [Accelerating Python](../advanced/python-optimization.md) — NumPy, Numba, multiprocessing, GPU

### Batch Job

```bash
#!/bin/bash
#SBATCH --job-name=python_job
#SBATCH --output=python_%j.out
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=2:00:00

module load miniconda

conda activate /path/to/myenv

python script.py
```

---

## R

### Batch Job

```bash
#!/bin/bash
#SBATCH --job-name=r_job
#SBATCH --output=r_%j.out
#SBATCH --partition=normal
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=4:00:00

module load R/4.5.0

Rscript analysis.R
```

### Interactive (RStudio via Open OnDemand)

[Open OnDemand](../gui-and-tools/open-ondemand.md) → Interactive Apps → RStudio Server — this is the easiest way to use R interactively.

---

## Need Help?

- **Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Support tickets**: [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)
