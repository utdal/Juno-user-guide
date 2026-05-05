# How to Log In to the System

## Overview

This guide covers the different methods to access Juno HPC cluster.

## SSH Login (Command Line)

### Basic Login

The primary method to access Juno is through SSH (Secure Shell).

**Linux/Mac**

Open your terminal and run:
```bash
ssh netID@juno.utdallas.edu
```
    
Replace `netID` with your assigned Juno username.

**Windows (PowerShell)**

Open PowerShell and run:
    
```bash
ssh username@juno.utdallas.edu
```

**Windows (PuTTY)**

1. Download and install [PuTTY](https://www.putty.org/)
2. Open PuTTY
3. Enter hostname: `juno.utdallas.edu`
4. Port: `22`
5. Connection type: SSH
6. Click "Open"
7. Enter your username and password when prompted

### First-Time Login

When logging in for the first time:

1. You'll see a message about host authenticity:
   ```
   The authenticity of host 'juno.utdallas.edu' can't be established.
   Are you sure you want to continue connecting (yes/no)?
   ```

2. Type `yes` and press Enter

3. Enter your password when prompted (characters won't appear as you type)

4. You should see the Juno welcome message and command prompt

**Login Node**

After successful login, you'll be on a **login node**. The prompt will show something like:
```
[netID@juno-l-01 ~]$
```

## SSH Key Authentication (Recommended)

For password-free login, set up SSH keys:

### Generate SSH Key Pair

**Linux/Mac**

```bash
# Generate key pair
ssh-keygen -t ed25519 -C "netID@utdallas.edu"
    
# Press Enter to accept default location
# Enter passphrase (optional but recommended)
    
# Copy public key to Juno
ssh-copy-id netID@juno.utdallas.edu
```

**Windows (PowerShell)**

```powershell
# Generate key pair
ssh-keygen -t ed25519 -C "your_email@utdallas.edu"
    
# Copy public key to Juno
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh netID@juno.utdallas.edu "cat >> .ssh/authorized_keys"
```

### Test SSH Key Login

```bash
ssh netID@juno.utdallas.edu
```

You should now log in without entering a password (only passphrase if you set one).

## Login with X11 Forwarding (for GUI)

To run graphical programs, use X11 forwarding:

### Prerequisites

**Mac**

1. Install [XQuartz](https://www.xquartz.org/)
2. Log out and back in (required after first install)
3. Open XQuartz terminal

**Windows**

1. Install [MobaXterm](https://mobaxterm.mobatek.net/) (Home Edition is free)
2. X server starts automatically
3. Use MobaXterm's built-in terminal

**Linux**

X11 is usually pre-installed. No additional software needed.

### Login with X11

```bash
ssh -X netID@juno.utdallas.edu
```


**NOTE:** Use capital `-X` (not lowercase `-x`)

### Test X11 Forwarding

After logging in with `-X`:

```bash
xclock
```

A clock window should appear on your local screen.

## Open OnDemand (Web Interface)

Access Juno through your web browser:

### Accessing Open OnDemand

1. Navigate to: [https://juno-ood.hpcre.utdallas.edu/](https://juno-ood.hpcre.utdallas.edu/)
2. Log in with your Juno credentials
3. You'll see the Open OnDemand dashboard

### Features Available

- **Files**: Browse and manage your files
- **Shell Access**: Web-based terminal
- **Interactive Apps**: Launch Jupyter, RStudio, MATLAB, etc.
- **Job Composer**: Create and submit jobs through GUI
- **Active Jobs**: Monitor your running jobs

**Tip:** Open OnDemand is perfect for users who prefer graphical interfaces or need to access Juno from networks that block SSH.

For detailed Open OnDemand usage, see [Launching GUI Programs](../gui-and-tools/gui-programs.md).

## Connection Issues

### Cannot Connect

**Check your network**:
```bash
ping juno.utdallas.edu
```

**Common issues**:

- **Off-campus**: You may need to use [VPN](https://atlas.utdallas.edu/TDClient/30/Portal/Requests/ServiceDet?ID=167)
- **Firewall**: SSH port 22 might be blocked
- **Incorrect hostname**: Verify `juno.utdallas.edu`

### Connection Timeout

If connection times out:

1. Verify you're on UT Dallas network or VPN
2. Check if SSH port 22 is accessible:
   ```bash
   telnet juno.utdallas.edu 22
   ```
3. Contact [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)

### Authentication Failed

**Wrong password**:
- Verify credentials
- Check Caps Lock
- Reset password if needed

**SSH key not working**:
```bash
# Check key permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### Connection Dropped

If your connection frequently drops:

**Use `tmux` or `screen`**:
```bash
# Start tmux session
tmux new -s mysession

# Your work continues even if disconnected
# Reconnect with:
tmux attach -t mysession
```

## Login Node Best Practices

**Important:**
    Login nodes are shared resources. **Do not run computational work on login nodes.**

**Acceptable on login nodes**:
- Editing files
- Compiling code
- Transferring small files
- Submitting jobs
- Light testing

**Not acceptable on login nodes**:
- Running simulations
- Processing large datasets
- Memory-intensive operations
- Long-running computations

For computational work, use [compute nodes via SLURM](../running-programs/slurm.md).

## Quick Reference

### Login Commands

| Purpose | Command |
|---------|---------|
| Basic login | `ssh netID@juno.utdallas.edu` |
| Login with X11 | `ssh -X netID@juno.utdallas.edu` |
| Specify SSH key | `ssh -i ~/.ssh/mykey netID@juno.utdallas.edu` |
| Keep connection alive | `ssh -o ServerAliveInterval=60 netID@juno.utdallas.edu` |

### Useful After Login

```bash
# Check your quota
mfsgetquota -H ~

# See who else is logged in
who

# Check system load
uptime

# View your jobs
squeue --me
```

## Next Steps

After successfully logging in:

1. [Explore storage options →](storage.md)
2. [Learn basic Linux commands →](../working-on-juno/linux-commands.md)
3. [Submit your first job →](../running-programs/slurm.md)

## Need Help?

- **Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **HPC Services**: [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)