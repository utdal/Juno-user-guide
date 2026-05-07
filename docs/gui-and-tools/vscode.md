# VSCode on Juno

## Overview

Visual Studio Code (VSCode) can be used to develop and edit code on Juno. There are two ways to do this:

1. **Open OnDemand** (recommended) — runs VSCode on a compute node with full resources
2. **Remote-SSH extension** (not recommended) — connects to a login node, which is limited to 8 GB RAM and may crash

**Use Open OnDemand.** The Remote-SSH approach connects to a login node, which has limited RAM (8 GB) and is not meant for running code or development tools.

## Why Use VSCode with Juno?

### Benefits

✓ **Local IDE experience** on remote HPC system  
✓ **Syntax highlighting** and IntelliSense  
✓ **Integrated terminal** for running commands  
✓ **File browser** for easy navigation  
✓ **Git integration** built-in  
✓ **Extensions** for Python, R, C++, Jupyter, and more  
✓ **Debug remotely** with breakpoints  
✓ **No X11** forwarding needed  

## Working with VSCode on Juno via Open OnDemand (Recommended)

1. Open your web browser
2. Navigate to: `https://juno-ood.hpcre.utdallas.edu/`
3. Log in with your Juno credentials
4. Click **Interactive Apps** in the top menu
5. Select your desired application (e.g., "Jupyter Notebook")
6. Fill in the resource request form:
   - **Number of hours**: How long you need (e.g., 2, 4, 8)
   - **Number of cores**: CPUs needed (typically 1-4 for interactive work)
   - **Memory (GB)**: RAM required (e.g., 4, 8, 16)
   - **Partition**: Usually "normal" for CPU, "h100" or "a30" for GPU work

7. Click **Launch**

8. Wait for resources to be allocated (you'll see status: Queued → Starting → Running)

9. Click **Connect to VSCode** when ready

![Screenshot of VSCode running in a browser via Open OnDemand, showing the file explorer sidebar, an open Python file with syntax highlighting, and the integrated terminal at the bottom.](../images/screenshot-ood-vscode.png)

### Opening Directories

**Open your project**:

1. File → Open Folder
2. Navigate to your project directory (e.g., `~/scratch/project`)
3. Click OK

**Or from terminal**:
```bash
# In VSCode terminal
code ~/scratch/project
```

### File Explorer

**Left sidebar**:

- Browse Juno filesystem
- Create/delete/rename files
- Drag and drop files
- Search files

**Right-click options**:

- Open in Terminal
- Reveal in File Explorer
- Copy Path
- Download (to local computer)

### Integrated Terminal

**Open terminal**:

- Press `` Ctrl+` `` (backtick)
- Or: View → Terminal
- Multiple terminals supported

**Use terminal for**:

- Running commands
- Submitting jobs
- Loading modules
- Git operations

### Editing Code

**Features**:

- Syntax highlighting (auto-detected)
- Auto-completion
- Code formatting
- Find and replace
- Multi-cursor editing

**Keyboard shortcuts**:

- `Ctrl+S`: Save
- `Ctrl+F`: Find
- `Ctrl+H`: Find and replace
- `Ctrl+/`: Toggle comment
- `Alt+Up/Down`: Move line

## Useful Extensions for HPC

### Python Development

**Python** (Microsoft):
```
# Install from Extensions
Search: Python
Publisher: Microsoft
```

**Features**:

- IntelliSense
- Linting
- Debugging
- Jupyter support

**Configure**:
```bash
# In VSCode terminal
which python  # Copy this path

# Set in VSCode:
# Ctrl+Shift+P → Python: Select Interpreter
# Paste the path
```

### Jupyter Notebooks

**Jupyter** (Microsoft):
```
Search: Jupyter
Publisher: Microsoft
```

**Open .ipynb files directly** in VSCode on Juno!

### Remote Development

**Remote - SSH** (not recommended for Juno):

The Remote-SSH extension connects to a login node, which only has 8 GB of RAM available for VSCode and its processes. This can cause VSCode to crash when handling large files, indexing projects, or running extensions. Use the Open OnDemand method above instead.

### Version Control

**GitLens**:
```
Search: GitLens
Publisher: GitKraken
```

**Features**:

- Enhanced Git integration
- Blame annotations
- File history
- Commit search

### Other Useful Extensions

**Markdown All in One**:

- Preview markdown files
- Useful for documentation

**YAML**:

- Syntax checking for YAML files
- Useful for configuration

**C/C++** (Microsoft):

- IntelliSense for C/C++
- Debugging support

## Running Jobs from VSCode

### Submit SLURM Jobs

**In integrated terminal**:
```bash

# Submit job
sbatch job_script.sh

# Monitor
squeue -u $USER

# View output
tail -f output_12345.log
```

### Interactive Development

**Request interactive resources**:
```bash
# In VSCode terminal
salloc -p normal --mem=8GB -c 4 -t 2:00:00
srun --pty bash

# Now on compute node
python my_script.py
```

**Or use task runner** (see Advanced section).

## Debugging on Juno

### Python Debugging

**Create launch.json**:

1. Run → Add Configuration
2. Select "Python File"
3. Edit `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

**Debug**:

- Set breakpoints (click left of line numbers)
- Press `F5` to start debugging
- Step through code with `F10`, `F11`

### C/C++ Debugging

**Install C/C++ extension**, then configure:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "(gdb) Launch",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/program",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb"
        }
    ]
}
```

## File Synchronization

### Automatic Sync

VSCode automatically syncs:

- Edits you make in VSCode
- File creation/deletion
- No manual upload needed

### Manual Download/Upload

**Download files**:

- Right-click file → Download
- Downloads to local computer

**Upload files**:

- Drag and drop into VSCode explorer
- Or use SCP/SFTP separately

### Using Git

**Best practice** for code:
```bash
# On Juno (in VSCode terminal)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/user/repo.git
git push -u origin main
```

## Advanced Features

### Port Forwarding

**Forward ports** to access web services:

1. Terminal → Ports tab
2. Click "Forward a Port"
3. Enter port number (e.g., 8888 for Jupyter)
4. Access at `localhost:8888` in local browser

**Example - Jupyter**:
```bash
# On Juno
module load miniconda
conda activate /path/to/myenv
jupyter notebook --no-browser --port=8888

# Forward port 8888 in VSCode
# Open localhost:8888 locally
```

### Task Runner

**Create tasks.json** for common commands:

`.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Submit Job",
            "type": "shell",
            "command": "sbatch",
            "args": ["${file}"],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Check Queue",
            "type": "shell",
            "command": "squeue",
            "args": ["-u", "$USER"]
        }
    ]
}
```

**Run task**: Terminal → Run Task → Select task

### Workspace Settings

**Save project-specific settings**:

`.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "/path/to/python",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    },
    "terminal.integrated.env.linux": {
        "MODULEPATH": "/path/to/modules"
    }
}
```

## Performance Tips

### Reduce Lag

**If experiencing lag**:

1. **Disable unused extensions** on remote
   - Extensions → Select extension → Disable (Workspace)

2. **Increase timeout**:
   - Settings → "Remote.SSH: Connect Timeout"
   - Increase to 60+ seconds

3. **Use stable connection**:
   - Wired connection preferred over WiFi
   - Use UT Dallas network or VPN

### Optimize File Watching

**For large directories**:

`.vscode/settings.json`:
```json
{
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/node_modules/**": true,
        "**/scratch/**": true
    }
}
```

## Troubleshooting

### Cannot Connect

**Check**:
```bash
# Test SSH connection
ssh netID@juno.utdallas.edu

# If fails, check:
# - VPN connected (if off-campus)
# - Correct username
# - SSH keys set up
```

### Connection Drops

**Solutions**:

1. Add to SSH config:
   ```
   ServerAliveInterval 60
   ServerAliveCountMax 3
   ```

2. Use tmux on Juno:
   ```bash
   tmux new -s vscode
   # Work continues even if connection drops
   ```

### "Too Many Authentication Failures"

**Solution**:

Add to SSH config:
```
Host juno
    IdentitiesOnly yes
    IdentityFile ~/.ssh/id_ed25519
```

### Extensions Not Working

**Install on SSH**:

- Extensions → Find extension
- Click "Install in SSH: juno"

### Python Interpreter Not Found

**Solution**:
```bash
# In VSCode terminal
which python

# Copy path and set:
# Ctrl+Shift+P → Python: Select Interpreter → Enter interpreter path
```

## Best Practices

### 1. Use Workspaces

Save workspace with specific settings:

- File → Save Workspace As
- Saves all open folders and settings

### 2. Version Control

**Always use Git**:

- Track changes
- Collaborate easily
- Backup code

### 3. Separate Code and Data

```
~/project/     # Code (Git tracked)
~/scratch/project/  # Data (not tracked)
```

### 4. Use .gitignore

Exclude unnecessary files:
```
# .gitignore
__pycache__/
*.pyc
*.log
*.out
*.err
data/
results/
```

### 5. Remote Extensions Only

Install extensions on SSH side only when needed:

- Reduces local resource usage
- Faster VSCode startup

## Example Workflows

### Python Development

1. Connect to Juno via VSCode
2. Open project folder
3. Create/edit Python scripts
4. Test in integrated terminal:
   ```bash
   python script.py
   ```
5. Submit as job when ready:
   ```bash
   sbatch job.sh
   ```

### C++ Development

1. Open project in VSCode
2. Edit source files
3. Compile in terminal:
   ```bash
   module load gnu14
   g++ -O3 program.cpp -o program
   ```
4. Debug with breakpoints
5. Submit parallel job when tested

### Jupyter Notebook

1. Open .ipynb file in VSCode
2. Select kernel (Python from Juno)
3. Run cells interactively
4. Convert to Python script for batch jobs

## Quick Reference

### Essential Shortcuts

```
F1 or Ctrl+Shift+P    Command Palette
Ctrl+`                Toggle Terminal
Ctrl+B                Toggle Sidebar
Ctrl+P                Quick File Open
Ctrl+Shift+F          Search in Files
Ctrl+Shift+G          Source Control
F5                    Start Debugging
Ctrl+S                Save
Ctrl+Shift+S          Save All
```

### Common Commands

```bash
# In VSCode Terminal
module load python/3.12.2    # Load software
sbatch job.sh             # Submit job
squeue -u $USER          # Check queue
tail -f output.log       # Monitor output
```

## Next Steps

- [Submit jobs from VSCode →](../running-programs/slurm.md)
- [Set up Python environments →](../advanced/miniconda.md)
- [Learn about containers →](../advanced/containers.md)

## Need Help?

- **VSCode issues**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Connection problems**: Check [Login Guide](../getting-started/login.md)
- **VSCode documentation**: [code.visualstudio.com/docs](https://code.visualstudio.com/docs)