# Launching GUI Programs (X11)

## Overview

Juno supports running graphical user interface (GUI) programs through two main methods:

1. **[Open OnDemand](open-ondemand.md)** — a web-based portal, recommended for most users
2. **X Window System** — traditional X11 forwarding, covered on this page

!!! tip "Looking for the web portal?"
    For most interactive GUI work, [Open OnDemand](open-ondemand.md) is easier — just a browser, no setup. Use X11 forwarding (below) when you need a specific GUI program that isn't available as an interactive app.

## X Window System (X11 Forwarding)

For users who prefer command-line access or need specific GUI programs not available in Open OnDemand.

### Prerequisites

Install an X server on your local computer:

**Mac**

**Install XQuartz**:
    
1. Download from [xquartz.org](https://www.xquartz.org/)
2. Install the .dmg file
3. **Log out and log back in** (required)
4. Open XQuartz
5. Use the XQuartz terminal for SSH

**Windows**

**Install MobaXterm** (Recommended):
    
1. Download from [mobaxterm.mobatek.net](https://mobaxterm.mobatek.net/)
2. Choose Home Edition (free)
3. Install the software
4. X server starts automatically with MobaXterm
5. Use MobaXterm's built-in terminal
    
**Alternative: Xming**:
    
1. Download [Xming](https://sourceforge.net/projects/xming/)
2. Install Xming
3. Start Xming from Start menu
4. Use PowerShell or PuTTY with X11 forwarding enabled

**Linux**

X11 is typically pre-installed. No additional software needed.

### Logging In with X11

```bash
ssh -X netID@juno.utdallas.edu
```

!!! note
    Use capital `-X` for X11 forwarding, not lowercase `-x`

**For slower connections, use compression**:
```bash
ssh -XC netID@juno.utdallas.edu
```

### Testing X11 Forwarding

After logging in with `-X`, test with a simple program:

```bash
xclock
```

If a clock appears on your screen, X11 forwarding is working correctly!

### Running GUI Programs on Login Node

!!! note
    Only use login nodes for quick tests or launching programs that will run on compute nodes.

```bash
# Test X11
xclock

# Launch MATLAB (from login node, not recommended for computation)
module load matlab/r2024b
matlab
```

### Running GUI Programs on Compute Nodes

**Recommended approach**: Request resources, then launch GUI program.


```bash
# Step 1: Request resources on login node
salloc -p normal --mem=8GB -c 4 -t 2:00:00

# Step 2: Check which nodes are assigned
squeue --me

# Step 3: Start interactive session with X11
ssh -X c-XX-YY             # Node c-XX-YY was assigned

# Now on compute node, launch GUI program
module load matlab/r2024b
matlab
```

Your prompt changes from `juno-l-01` to `c-XX-YY`, indicating you're on a compute node.


### Common GUI Applications

#### MATLAB

```bash
# Load MATLAB module
module load matlab/r2024b

# Launch MATLAB GUI
matlab

# Or run MATLAB script without GUI
matlab -nodisplay -nosplash -r "run('script.m'); exit;"
```

#### Ansys Fluent

```bash
module load ansys/2025R1
fluent
```

#### Stata

```bash
module load stata/19.5
xstata

```

### Troubleshooting X11

#### "Cannot open display" error

**Problem**: X11 forwarding not working

**Solutions**:

1. **Verify X server is running** on your local machine
   - Mac: Check XQuartz is running
   - Windows: Check MobaXterm or Xming is running

2. **Check DISPLAY variable**:
   ```bash
   echo $DISPLAY
   ```
   Should show something like `localhost:10.0`

3. **Re-login with -X flag**:
   ```bash
   ssh -X netID@juno.utdallas.edu
   ```

4. **Try -Y instead of -X** (Mac users):
   ```bash
   ssh -Y netID@juno.utdallas.edu
   ```

5. **Check SSH config**:
   Add to `~/.ssh/config` on your local machine:
   ```
   Host juno
       HostName juno.utdallas.edu
       User your_username
       ForwardX11 yes
       ForwardX11Trusted yes
   ```

#### Slow Performance

**Problem**: GUI is laggy or unresponsive

**Solutions**:

1. **Enable compression**:
   ```bash
   ssh -XC netID@juno.utdallas.edu
   ```

2. **Reduce color depth** (if using VNC/remote desktop)

3. **Consider using Open OnDemand** instead (better for slow connections)

4. **Close unnecessary windows and programs**

#### X11 Works on Login but Not Compute Node


**Solution**: Use `-X` flag when you log in to the compute node:
```bash
ssh -X c-XX-YY
```

### X11 Configuration Tips

#### SSH Config File

Create `~/.ssh/config` on your local machine:

```
Host juno
    HostName juno.utdallas.edu
    User your_username
    ForwardX11 yes
    ForwardX11Trusted yes
    Compression yes
```

Now you can simply:
```bash
ssh juno
```

#### Keep Connection Alive

Add to SSH config:
```
Host juno
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

---

## Best Practices

1. **Choose the right method**:
   - [Open OnDemand](open-ondemand.md) for most interactive work
   - X11 for specialized programs not in OnDemand

2. **Request appropriate resources**:
   - Start with modest requests (2-4 cores, 8GB RAM)
   - Scale up if needed

3. **End sessions when done**:
   - Don't leave interactive sessions running unnecessarily
   - Fair share applies to interactive jobs too

4. **Test on login node first** (briefly):
   - Verify program launches
   - Then move to compute nodes

5. **Use tmux/screen with X11**:
   ```bash
   # Start tmux before requesting resources
   tmux new -s gui_session
   salloc ...
   ```

## Example Workflow: MATLAB with X11

1. Open XQuartz terminal (Mac) or MobaXterm (Windows)
2. `ssh -X netID@juno.utdallas.edu`
3. `salloc -p normal --mem=16GB -c 4 -t 4:00:00`
4. `squeue --me`
5. `ssh -X c-XX-YY`
6. `module load matlab/r2024b`
7. `matlab`
8. Work in MATLAB GUI
9. Exit MATLAB
10. `exit` from compute node
11. `exit` from login node

For interactive-app workflows (Jupyter, RStudio), see [Open OnDemand](open-ondemand.md).

## Next Steps

- [Use the Open OnDemand web portal →](open-ondemand.md)
- [Set up VSCode for remote development →](vscode.md)
- [Learn about containerized applications →](../advanced/containers.md)
- [Optimize your interactive workflows →](../running-programs/slurm.md)

## Need Help?

- **Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **HPC Services**: [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)
- **Open a ticket**: For specific GUI application requests or issues