# Juno HPC Cluster User Guide

## Introduction

Welcome to Juno, the flagship High Performance Computing (HPC) cluster at UT Dallas. This guide provides essential information for new users to get started with the system.

## What is Juno?

Juno is a high performance computing cluster consisting of multiple computers (nodes) that work together to run programs efficiently. Each individual computer in the cluster is called a **node**.

### Cluster Components

The cluster contains **104 nodes** organized into four types:

- **CPU compute nodes**: 94 nodes with 2× AMD EPYC CPUs (64 cores, 384 GB RAM each)
- **GPU compute nodes**: 7 nodes with NVIDIA H100 or A30 GPUs
- **Login nodes**: Your entry point to the cluster (2 nodes, `juno-l-01` and `juno-l-02`)
- **Head node**: Where the job scheduler (SLURM) is hosted

All compute nodes are interconnected via HDR100 InfiniBand for fast MPI communication.

![Juno Cluster Diagram](images/Juno.png)

For full hardware specifications, see the [Hardware Overview](getting-started/hardware.md).

---

## Quick Start Guide

<div class="grid cards" markdown>

-   **Get Started**

    ---

    Request an account and learn how to log in to Juno

    [Request Account](getting-started/account-request.md)

-   **SLURM Job Scheduler**

    ---

    Learn to submit and manage jobs on the cluster

    [SLURM Guide](running-programs/slurm.md)

-   **GUI Programs**

    ---

    Launch graphical applications using Open OnDemand or X11

    [GUI Guide](gui-and-tools/gui-programs.md)

-   **Get Help**

    ---

    Contact support and find answers to common questions

    [Support](support/getting-help.md)

</div>

---

## Documentation Overview

### Getting Started
New to Juno? Start here to set up your account, log in, and understand the storage system.

- [How to Request an Account](getting-started/account-request.md)
- [How to Log In to the System](getting-started/login.md)
- [SSH Key Authentication](getting-started/ssh-keys.md)
- [Storage and Data Transfer](getting-started/storage.md)
- [Scratch Space](getting-started/scratch-space.md)
- [Hardware Overview](getting-started/hardware.md)

### Working on Juno
Learn the essential tools and commands for working on the cluster.

- [Linux Commands Crash Course](working-on-juno/linux-commands.md)
- [Module System](working-on-juno/modules.md)
- [Available Software and Compilers](working-on-juno/software.md)

### Running Programs
Master job submission and execution on Juno.

- [SLURM Job Scheduler](running-programs/slurm.md)
- [Monitoring Jobs and Cluster State](running-programs/advanced-slurm.md)
- [Running Common Scientific Programs](running-programs/common-programs.md)
- [Parallelism Models](running-programs/parallelism.md)
- [High Throughput Processing with Launcher](running-programs/launcher.md)

### AI & Machine Learning
Run GPU workloads, train PyTorch models, and optimize GPU performance.

- [GPU Computing on Juno](ai-and-ml/index.md)
- [PyTorch Training Jobs](ai-and-ml/pytorch-training.md)
- [GPU Performance & Monitoring](ai-and-ml/gpu-performance.md)

### GUI & Development Tools
Access graphical interfaces and modern development environments.

- [Launching GUI Programs](gui-and-tools/gui-programs.md)
- [JupyterLab on Juno](gui-and-tools/jupyter.md)
- [VSCode on Juno](gui-and-tools/vscode.md)

### Advanced Topics
Optimize your workflows with advanced techniques.

- [Containers on Juno](advanced/containers.md)
- [Accelerating Python](advanced/python-optimization.md)
- [Virtual Environments with Miniconda](advanced/miniconda.md)

### Support & FAQ
Get help and find answers to common questions.

- [Getting Help](support/getting-help.md)
- [Frequently Asked Questions](support/faq.md)

---

## Important Links

- **HPC Services**: [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)
- **Support Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Orientation Slides**: Available on the HPC documentation website

---

*For the most current information, always refer to the official HPC documentation at hpc.utdallas.edu.*