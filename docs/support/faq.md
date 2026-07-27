# Frequently Asked Questions (FAQ)

## Account & Access

### How do I request a Juno account?

See the [Account Request Guide](../getting-started/account-request.md) for detailed instructions. Students need faculty sponsor approval and their PI must have an existing account on Juno. Faculty and staff can request directly.

### I forgot my username. How do I find it?

Your Juno username is typically your NetID. Email [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu) with your full name for confirmation.

### Can I access Juno from off-campus?

Yes, but you may need to use the UT Dallas VPN for SSH access. See [VPN setup guide](https://atlas.utdallas.edu/TDClient/30/Portal/Requests/ServiceDet?ID=167).

### How do I reset my password?

Your password is associated with your NetID password. Please follow [these instructions](https://atlas.utdallas.edu/TDClient/30/Portal/KB/ArticleDet?ID=1262) to reset or recover your password.

### My account is locked. What do I do?

This usually happens after multiple failed login attempts. Email [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu) immediately to have it unlocked.

---

## Storage & Data

### Where should I store my data?

| Location | Path | Shared with G2 | Best For |
|----------|------|----------------|----------|
| Home (Io) | `~` | No | Config files, scripts, small data |
| Work (Io) | `~/work` | No (Juno only) | Large software, data, results |
| Group (Io) | `/groups/<pi-name>` | **Yes** | Shared group data |
| Scratch | `~/scratch` | **Yes** | High-speed I/O during batch jobs |

See the [Storage Guide](../getting-started/storage.md) for details.

### Can I get to my Juno data from Ganymede 2?

Yes, for `/groups/<pi-name>` and `~/scratch` — those are the **same filesystems** on both clusters, with a shared quota, so no copying is needed. Your home directory is separate per cluster, and `~/work` exists only on Juno (on G2, use `/groups/<pi-name>` instead).

### What's my storage quota?

Check your current usage and quota:
```bash
mfsgetquota -H ~           # Home: 50 GB
mfsgetquota -H ~/work      # Work: 1 TB
mfsgetquota -H /groups/groupname   # Group: varies
```

Contact support if you need a quota increase.

### How do I transfer large files to Juno?

**Best options**:

- **rsync**: For synchronization
- **scp/sftp**: For smaller transfers

See [Storage and Data Transfer](../getting-started/storage.md).

### Are my files backed up?

Home, work, group directories are backed up daily. Scratch space is **NOT backed up** and may be purged. Always keep important data copies elsewhere.

### My files disappeared from scratch! What happened?

Scratch space has an automatic purge policy. Files not accessed for 45 days may be deleted. This is normal and expected. Never rely on scratch for permanent storage.

---

## SLURM & Job Scheduling

### How long does it take for my fair share to recover?

It takes **two weeks** of non-use to fully restore your fair share to 1.0. Your fair share value also recovers to full at the beginning of the month.

### Why is my job pending for so long?

Check the reason with:
```bash
squeue --me
```

Common reasons:

- **Resources**: No available nodes with requested resources
- **Priority**: Other jobs have higher priority (fair share)
- **QOSLimit**: You've hit resource limits

**Solution**: Reduce resource requests or wait for fair share to recover.

### How can I minimize my wait time and get resources faster?

Right-size your request (memory, cores, and `--time`), check what's free before submitting (`sinfo -t idle,mix`), and let your job run on more than one partition (`sbatch -p normal,dev job.sh`). Accurate requests are easier for the scheduler to backfill and keep your fair-share score high.

For the full set of tips — including the `cluster_monitor.py` script that shows live CPU, memory, requestable-memory and GPU utilization for every node — see [Tips: Minimizing Wait Time and Getting Resources Faster](../running-programs/advanced-slurm.md#tips-minimizing-wait-time-and-getting-resources-faster).

### Can I run programs directly on the login node?

Only for **light tasks**:

- ✓ Editing files
- ✓ Compiling code  
- ✓ Small file operations
- ✓ Submitting jobs

**Never** on login nodes:

- ✗ Running simulations
- ✗ Processing large datasets
- ✗ Long-running computations

Use [compute nodes via SLURM](../running-programs/slurm.md) for computational work.

### How do I check if my job completed successfully?

```bash
# Check job status
sacct -j JOBID

# Look at output files
cat output_JOBID.txt
cat error_JOBID.txt
```

Exit code 0 means success. Non-zero indicates an error.

### What's the difference between `salloc` and `sbatch`?

- **`salloc`**: Interactive sessions - you type commands in real-time
- **`sbatch`**: Batch jobs - runs a script unattended

See [SLURM Guide](../running-programs/slurm.md) for examples.

### My job was killed with "Out of Memory". What now?

Increase memory request:
```bash
#SBATCH --mem=32GB  # Instead of 16GB
```

Or check your program for memory leaks.

### How do I request GPU resources?

```bash
#SBATCH -p h100                 # or h200, a30, a30-2.12gb, a30-4.6gb
#SBATCH --gres=gpu:1            # Request 1 GPU
```

Choose the partition based on your VRAM needs:

| Partition | GPU | VRAM |
|-----------|-----|------|
| `h200` | H200 NVL (physical) | 141 GB |
| `h100` | H100 (physical or half-slice) | 80 GB, 94 GB NVL, or 47 GB half |
| `a30` | A30 (physical) | 24 GB |
| `a30-2.12gb` | A30 (virtual half) | 12 GB |
| `a30-4.6gb` | A30 (virtual quarter) | 6 GB |

See [SLURM Guide](../running-programs/slurm.md) for GPU job examples.

### Can I run multiple jobs simultaneously?

Yes. Per-user limits are:

- **Max 4 running jobs** at a time
- **Max 8 submitted jobs** (queued + running)

These limits can be relaxed for specific projects — contact support with evidence of efficient resource utilization.

### How do I cancel all my jobs at once?

```bash
scancel -u $USER
```

---

## Software & Modules

### How do I find available software?

```bash
# List all available modules
module avail

# Search for specific software
module avail ansys
```

### How do I load software?

```bash
module load matlab
```

Check [Module System Guide](../working-on-juno/modules.md).

### The software I need isn't available. What do I do?

1. Check if you can install it locally in your home directory
2. Use containers (Apptainer)
3. Request installation via [support ticket](../support/getting-help.md)

### Can I install my own software?

Yes! You can install software in:

- Your home directory: `$HOME/software` (not recommended due to limited space)
- Your work and group directories (recommended) using:
    - Conda/mamba environments (recommended)
    - Python virtual environments
    - Containers

See [Software Guide](../working-on-juno/software.md).

### Do I need to load modules every time I log in?

Some modules are loaded by default (GNU 12, OpenMPI 4, and a few system modules). For other software, yes — load them explicitly. Add `module load` commands to your job scripts rather than your `.bashrc`, to avoid unexpected conflicts.

### Two modules conflict. How do I resolve this?

```bash
# Unload conflicting module
module unload old-version

# Load new version
module load new-version
```

Or use `module purge` to start fresh.

---

## GUI & Interactive Work

### Can I use Jupyter notebooks on Juno?

Yes! Use [Open OnDemand](../gui-and-tools/open-ondemand.md):
1. Interactive Apps → JupyterLab
2. Request resources
3. Connect when ready

### How do I run MATLAB with a graphical interface?

**Option 1 (Recommended)**: Open OnDemand

**Option 2**: X11 forwarding with `ssh -X`

See [GUI Programs Guide](../gui-and-tools/gui-programs.md).

### X11 forwarding isn't working. What's wrong?

**Check**:

1. X server running on your computer (XQuartz/MobaXterm)
2. Logged in with `ssh -X` (capital X)
3. Test with `xclock`

Mac users: Try `ssh -Y` instead of `ssh -X`

See [troubleshooting section](../gui-and-tools/gui-programs.md#troubleshooting-x11).

### Can I use VSCode on Juno?

Yes! Launch VSCode through Open OnDemand so it runs on a compute node with full resources. (Avoid the Remote-SSH extension, which connects to a memory-limited login node.) See [VSCode Guide](../gui-and-tools/vscode.md).

---

## Performance & Optimization

### My code is running slow. How do I speed it up?

1. Check if your code can use multiple CPUs (parallelize)
2. Request appropriate resources
3. Use optimized libraries (MKL, OpenBLAS)
4. Profile your code to find bottlenecks
5. Consider GPU acceleration if applicable

Request a [consultation](../support/getting-help.md) for optimization help.

### Should I request more CPUs or more memory?

Depends on your workload:

- **CPU-bound**: Computation-heavy → request more CPUs
- **Memory-bound**: Large datasets → request more memory

Monitor with `jobstats JOBID` after jobs complete (run `module load jobstats` first). See [Monitoring Jobs and Cluster State](../running-programs/advanced-slurm.md).

### How many CPUs should I request?

Start with what your program can effectively use:

- Serial programs: 1 CPU
- Parallel programs: Check documentation for scaling
- Don't request more than your code can utilize

### What's the maximum time I can request?

Varies by partition. Check with:
```bash
sinfo -o "%P %l"
```

Typical limits: 2-48 hours depending on partition.

---

## Python & R

### How do I use Python packages?

**Options**:

1. Load system Python module + pip install to home
2. Use conda environments (recommended)
3. Use Python virtual environments

See [Miniconda Guide](../advanced/miniconda.md).

### Can I use conda on Juno?

Yes! Load the system Miniconda module with `module load miniconda` — no install needed. Create environments in `~/work` or `/groups` (not home, which has limited space). See the [Virtual Environments guide](../advanced/miniconda.md).

### My Python job failed with "ModuleNotFoundError"

**Solutions**:

1. Install missing package: `pip install package-name`
2. Load appropriate Python module
3. Activate correct conda environment

### How do I use R packages?

```bash
# Load R module
module load R

# In R:
install.packages("package_name", repos="http://cran.us.r-project.org")
```

Or use RStudio via Open OnDemand.

---

## Troubleshooting

### My job won't start. What's wrong?

**Check**:

1. Resource availability: `sinfo`
2. Your fair share: `sshare`
3. Job queue position: `squeue --me`
4. Job script syntax: Look for SBATCH errors in output

### I can't log in. What should I do?

**Try**:

1. Verify you're using correct username/hostname
2. Check if you need VPN (off-campus)
3. Test internet connection: `ping juno.utdallas.edu`
4. Contact [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)

### My files have wrong permissions. How do I fix them?

```bash
# Make file readable/writable by you only
chmod 600 filename

# Make directory accessible
chmod 700 directory

# Make script executable
chmod +x script.sh
```

### I accidentally deleted important files! Can they be recovered?

**Home/work/group directory**: Possibly - contact support immediately

**Scratch space**: Likely not - scratch is not backed up

Prevention: Regular backups to external storage.

### Connection keeps dropping. What can I do?

**Use `tmux` or `screen`**:
```bash
# Start tmux session
tmux new -s mysession

# Work as normal
# If disconnected, reconnect with:
tmux attach -t mysession
```

Or add to `~/.ssh/config`:
```
Host juno
    ServerAliveInterval 60
```

---

## Best Practices

### What are some general best practices?

1. **Test small first**: Run short test jobs before large ones
2. **Monitor resources**: Use `jobstats` to check efficiency
3. **Clean up**: Remove old output files regularly
4. **Document**: Comment your code and scripts
5. **Version control**: Use git for code
6. **Backup**: Keep copies of important data
7. **Ask early**: Don't struggle - contact support

### How can I be a good cluster citizen?

1. Request only resources you need
2. Don't run on login nodes
3. Clean up scratch space
4. Cancel jobs you don't need
5. End interactive sessions when done
6. Share storage responsibly

### Should I run many small jobs or one big job?

Depends on your workflow:

- **Independent tasks**: Use job arrays (more efficient)
- **Sequential pipeline**: One job with dependencies
- **True parallel work**: One large parallel job

See [High Throughput guide](../running-programs/launcher.md).

---

## Policy Questions

### What's the acceptable use policy?

Resources must be used for:

- Academic research
- Coursework (if approved)
- UT Dallas affiliated work

Not allowed:

- Personal projects
- Commercial work (without agreement)
- Cryptocurrency mining
- Violation of laws or university policies

### Can I share my account?

**No.** Account sharing is prohibited. If collaborators need access, they should request their own accounts.

### How long does my account remain active?

- **Faculty/Staff**: While employed at UT Dallas
- **Students**: While enrolled (may need annual renewal)
- **Inactive accounts** (6+ months no login) may be deactivated

### What happens when I graduate/leave?

Notify HPC support. You'll have grace period to:

- Download data
- Complete ongoing computations
- Transfer projects to another user

---

## Still Have Questions?

Can't find your answer here? 

- [Open a support ticket](../support/getting-help.md)
- Email [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- Check the full [documentation](https://hpc.utdallas.edu)

---

!!! tip
    Before asking, try:

    1. Searching this FAQ
    2. Checking relevant guide sections
    3. Looking at error messages carefully
    4. Testing simple cases

When you do ask, provide details: job IDs, error messages, what you've tried. This helps us help you faster!