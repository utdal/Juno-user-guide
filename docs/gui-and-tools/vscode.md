# VSCode on Juno

## Overview

Visual Studio Code can run on Juno through **Open OnDemand**, which launches a browser-based VSCode (`code-server`) on a compute node with full CPU, memory, and GPU resources.

!!! warning "Use Open OnDemand, not Remote-SSH"
    The VSCode **Remote-SSH** extension connects to a **login node**, which is limited to ~8 GB of RAM and is not meant for running code or development tools. Indexing a project, opening large files, or running extensions there can crash your session and degrade the login node for everyone. Always use the Open OnDemand method below.

## Why VSCode on Juno?

- Full IDE experience (syntax highlighting, IntelliSense, search) on the cluster
- Integrated terminal for loading modules and submitting jobs
- File browser for the Juno filesystem
- Built-in Git integration and Jupyter notebook support
- No X11 forwarding required

## Launching VSCode via Open OnDemand

1. Open your browser and go to [https://juno-ood.hpcre.utdallas.edu/](https://juno-ood.hpcre.utdallas.edu/) (connect to the UT Dallas VPN first if off-campus).
2. Log in with your UT Dallas NetID.
3. Click **Interactive Apps** → **VSCode Server**.
4. Fill in the resource form:
   - **Number of hours** — how long you need (e.g. 4)
   - **Number of cores** — typically 2–4 for interactive work
   - **Memory (GB)** — e.g. 8–16
   - **Partition** — `normal` for CPU work, `h100` or `a30` for GPU work
5. Click **Launch** and wait for the status to reach **Running**.
6. Click **Connect to VSCode**.

![Screenshot of VSCode running in a browser via Open OnDemand, showing the file explorer sidebar, an open Python file with syntax highlighting, and the integrated terminal at the bottom.](../images/screenshot-ood-vscode.png)

For general Open OnDemand usage (managing sessions, file uploads), see [Launching GUI Programs](gui-programs.md).

## Working in VSCode

### Open your project

**File → Open Folder**, then navigate to your project (e.g. `~/scratch/project` or `~/work/project`).

### Integrated terminal

Press `` Ctrl+` `` to open a terminal **on the compute node**. Use it to load modules, activate environments, and submit jobs:

```bash
module load miniconda
conda activate /path/to/myenv
sbatch job.sh
squeue --me
```

### Select the Python interpreter

Point VSCode at the Python from your environment so IntelliSense and the debugger use the right packages:

```bash
# In the integrated terminal, find the interpreter path:
which python
```

Then run **Ctrl+Shift+P → Python: Select Interpreter** and paste that path.

## Accessing web services (port forwarding)

VSCode can forward a port from the compute node to your browser — useful for Jupyter, TensorBoard, or other web UIs:

1. Open the **Ports** tab in the terminal panel and click **Forward a Port**.
2. Enter the port (e.g. `8888`).
3. Open the forwarded URL VSCode provides.

For a full JupyterLab setup, see [JupyterLab on Juno](jupyter.md).

## Best Practices

- **Separate code and data**: keep Git-tracked code in `~/work` or `~`, and large data/outputs in `~/scratch`.
- **Use Git** for code, with a `.gitignore` that excludes `__pycache__/`, `*.pyc`, logs, and data directories.
- **Request only the resources you need**, and end the session when finished so resources return to the pool.
- **Develop interactively, then submit as a batch job** for long runs — don't run multi-hour computations in the interactive session.

For VSCode features not covered here (debugging, extensions, keybindings), see the official [VSCode documentation](https://code.visualstudio.com/docs).

## Troubleshooting

- **Session won't start / stuck queued** — the cluster may be busy; check `sinfo` for free nodes or reduce your resource request.
- **Python interpreter not found** — run `which python` in the integrated terminal and set it via **Python: Select Interpreter**.
- **Laggy interface** — use a wired connection or the UT Dallas VPN; close unused editor tabs.

## Next Steps

- [Submit jobs from the integrated terminal →](../running-programs/slurm.md)
- [Set up Python environments →](../advanced/miniconda.md)
- [Run JupyterLab on Juno →](jupyter.md)

## Need Help?

- **VSCode issues**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Connection problems**: see the [Login Guide](../getting-started/login.md)
