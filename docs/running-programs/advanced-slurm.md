# Monitoring Jobs and Cluster State

## Overview

This page covers the commands used to inspect the cluster, understand job details, and analyze completed job performance. These tools complement the basics covered in the [SLURM Job Scheduler](slurm.md) page.

---

## Checking Cluster Availability — `sinfo`

`sinfo` shows the state of every partition and node. Run it before submitting to find available resources.

```bash
$ sinfo
PARTITION    AVAIL  TIMELIMIT  NODES  STATE NODELIST
normal*         up 2-00:00:00      4  drng@ c-06-[05-07,10]
normal*         up 2-00:00:00      3  drain c-04-02,c-06-[09,11]
normal*         up 2-00:00:00     16    mix c-01-[04-05,07-09],c-02-[08,13,17],c-03-[01,04-05,07],c-04-[01,04],c-05-09,c-06-08
normal*         up 2-00:00:00     55  alloc c-01-[06,10-17],c-02-[07,09-12,14-16,18],c-03-[02-03,06,08-18],c-04-[03,05-18],c-05-[01-08]
normal*         up 2-00:00:00      1   idle c-01-18
...
h100            up 2-00:00:00      3    mix g-04-02,g-05-01,g-06-01
a30             up 2-00:00:00      2   mix- g-01-01,g-02-01
dev             up    2:00:00      1  inval c-02-06
dev             up    2:00:00      5   idle c-02-[01-05]
```

### Node States

| State | Meaning |
|---|---|
| `idle` | Node is free — no jobs running, ready to accept work |
| `alloc` | Node is fully allocated — all CPUs/GPUs are in use |
| `mix` | Node is partially allocated — some CPUs or memory are still free |
| `drain` | Administrator has marked the node to stop accepting new jobs (e.g., for maintenance); existing jobs continue running |
| `drng` | Node is draining and jobs are still completing |
| `drng@` | Node is draining and not responding to SLURM (may be rebooting or unreachable) |
| `mix-` | Node is partially allocated and has a reservation or planned state |
| `down` | Node is down and unavailable |
| `inval` | Node is in an invalid state (usually temporary during boot or reconfiguration) |

!!! tip
    Jobs can be submitted to nodes in `mix` state — SLURM will place them on free slots. Only `idle` and `mix` nodes will accept new jobs.

### Useful `sinfo` Variants

```bash
# Show only nodes with free resources
sinfo -t idle,mix

# Show GPU partitions only
sinfo -p h100,a30,a30-2.12gb,a30-4.6gb

# One line per node (useful for detailed view)
sinfo -N -l

# Custom format: partition, state, free memory, node name
sinfo -o "%.15P %.5a %.10l %.6D %.5t %.10m %N"

# Show time limits for all partitions
sinfo -o "%P %l"
```

---

## Inspecting a Partition — `scontrol show partition`

To see the full configuration of a partition, including time limits, allowed accounts, and total resources:

```bash
$ scontrol show partition h100
PartitionName=h100
   AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
   AllocNodes=ALL Default=NO QoS=juno
   DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
   MaxNodes=UNLIMITED MaxTime=2-00:00:00 MinNodes=0 LLN=NO MaxCPUsPerNode=UNLIMITED
   Nodes=g-04-02,g-05-01,g-06-01
   PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=192 TotalNodes=3
   TRES=cpu=192,mem=1500G,node=3,billing=192,gres/gpu=7,gres/gpu:nvidia_h100_80gb_hbm3=4,gres/gpu:nvidia_h100_nvl=3
```

**Key fields:**

| Field | Meaning |
|---|---|
| `MaxTime` | Wall-time limit for jobs in this partition |
| `Nodes` | Which nodes belong to this partition |
| `OverSubscribe` | Whether nodes can run more tasks than CPUs (`NO` = strict) |
| `PreemptMode` | What happens to lower-priority jobs if a higher one needs resources |
| `TRES` | Total resources in the partition (CPUs, memory, GPUs) |
| `QoS` | Quality of service policy applied to jobs in this partition |

---

## Inspecting a Node — `scontrol show node`

To see the current resource allocation and hardware details of a specific node:

```bash
$ scontrol show node g-04-02
NodeName=g-04-02 Arch=x86_64 CoresPerSocket=32
   CPUAlloc=36 CPUEfctv=64 CPUTot=64 CPULoad=31.02
   Gres=gpu:nvidia_h100_80gb_hbm3:4(S:0-1)
   NodeAddr=g-04-02 NodeHostName=g-04-02 Version=24.11.5
   OS=Linux 5.14.0-503.40.1.el9_5.x86_64
   RealMemory=512000 AllocMem=327680 FreeMem=390855 Sockets=2 Boards=1
   State=MIXED+RESERVED ThreadsPerCore=1 TmpDisk=0
   Partitions=h100
   BootTime=2026-05-02T04:14:16 SlurmdStartTime=2026-05-05T11:14:57
   CfgTRES=cpu=64,mem=500G,billing=64,gres/gpu=4,gres/gpu:nvidia_h100_80gb_hbm3=4
   AllocTRES=cpu=36,mem=320G,gres/gpu=4,gres/gpu:nvidia_h100_80gb_hbm3=4
   ReservationName=czhang
```

**Key fields:**

| Field | Meaning |
|---|---|
| `CPUAlloc` / `CPUTot` | CPUs currently in use vs. total available (36/64 here) |
| `CPUEfctv` | Effective CPUs visible to SLURM (may differ from physical if hyperthreading is off) |
| `CPULoad` | Current load average on the node |
| `RealMemory` / `AllocMem` / `FreeMem` | Total / allocated / physically free memory in MB |
| `Gres` | GPU resources on the node and which socket they are attached to |
| `CfgTRES` / `AllocTRES` | Total configured vs. currently allocated trackable resources |
| `State` | Node state (see [state table above](#node-states)); `RESERVED` means a reservation is active |
| `ReservationName` | Active reservation holding resources on this node |

This is useful for finding out why a node shows as `mix` — you can see exactly how many CPUs and how much memory are still free.

---

## Inspecting a Running or Pending Job — `scontrol show job`

```bash
$ scontrol show job 186552
JobId=186552 JobName=TESS_EBs_5_5-3
   UserId=utd000000(123456) GroupId=ph(333) MCS_label=N/A
   Priority=1305 Nice=0 Account=hpcre QOS=normal
   JobState=RUNNING Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=1-23:54:15 TimeLimit=2-00:00:00 TimeMin=N/A
   SubmitTime=2026-04-30T22:01:03 EligibleTime=2026-05-04T09:49:15
   StartTime=2026-05-04T10:04:23 EndTime=2026-05-06T10:04:23 Deadline=N/A
   Partition=normal AllocNode:Sid=juno-l-02:3809088
   NodeList=c-02-14,c-03-[12-18]
   BatchHost=c-02-14
   NumNodes=8 NumCPUs=512 NumTasks=8 CPUs/Task=64
   ReqTRES=cpu=512,mem=3000G,node=8,billing=512
   AllocTRES=cpu=512,mem=3000G,node=8,billing=512
   MinCPUsNode=64 MinMemoryNode=375G MinTmpDiskNode=0
   Command=/home/utd000000/projects/git/pipeline/slurm/juno/job.slurm
   WorkDir=/scratch/juno/utd000000/pipeline/juno/output
   StdErr=/scratch/juno/utd000000/output/pipeline/render_output/slurm.out
   StdOut=/scratch/juno/utd000000/output/pipeline/render_output/slurm.out
   MailUser=utd000000@utdallas.edu MailType=INVALID_DEPEND,BEGIN,END,FAIL,REQUEUE,STAGE_OUT
```

**Key fields:**

| Field | Meaning |
|---|---|
| `JobState` | Current state: `RUNNING`, `PENDING`, `COMPLETING`, `FAILED`, `TIMEOUT`, `CANCELLED` |
| `Reason` | For pending jobs, why the job hasn't started (e.g., `Resources`, `Priority`) |
| `Priority` | Scheduler priority score — higher means it runs sooner |
| `RunTime` / `TimeLimit` | How long the job has been running vs. its wall-time limit |
| `SubmitTime` / `EligibleTime` / `StartTime` | Timeline: when submitted, when it became eligible (dependencies cleared), when it started |
| `EligibleTime` | If this is much later than `SubmitTime`, the job was held in queue (e.g., waiting for fairshare) |
| `NodeList` | Compute nodes allocated to the job |
| `NumNodes` / `NumCPUs` / `NumTasks` | Resource allocation summary |
| `ReqTRES` / `AllocTRES` | Requested vs. actually allocated resources |
| `WorkDir` | Directory the job script runs in |
| `Command` | Path to the submitted job script |
| `StdOut` / `StdErr` | Output and error log file paths |

**For your own jobs**, this is the fastest way to find the log file path if you forgot where you set it:

```bash
scontrol show job $JOBID | grep StdOut
```

### Modifying a Pending Job

You can update certain properties of a job that hasn't started yet:

```bash
# Extend time limit
scontrol update JobId=12345 TimeLimit=3-00:00:00

# Change memory
scontrol update JobId=12345 MinMemoryNode=64G

# Hold and release
scontrol hold 12345
scontrol release 12345
```

---

## Job Accounting — `sacct`

`sacct` queries the job accounting database for completed, failed, and running jobs. It is the primary tool for checking exit codes, memory usage, and elapsed time after a job finishes.

```bash
$ sacct -j 186552 --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS,MaxVMSize
JobID           JobName      State ExitCode    Elapsed     MaxRSS  MaxVMSize
------------ ---------- ---------- -------- ---------- ---------- ----------
186552       TESS_EBs_+    TIMEOUT      0:0 2-00:00:13
186552.batch      batch  CANCELLED     0:15 2-00:00:14     24092K          0
```

Each job appears as multiple rows:
- The **top-level row** (just the job ID) summarizes the job as a whole
- The **`.batch` step** represents the batch shell script itself — this is where `MaxRSS` is recorded
- Additional steps (`.0`, `.1`, …) appear if the job used `srun` internally

**Key fields:**

| Field | Meaning |
|---|---|
| `State` | Final job state (`COMPLETED`, `FAILED`, `TIMEOUT`, `CANCELLED`, `OUT_OF_MEMORY`) |
| `ExitCode` | Exit code in `signal:code` format. `0:0` = clean exit. Non-zero signal means the job was killed by a signal (e.g., `0:9` = killed by SIGKILL, often OOM) |
| `Elapsed` | Total wall time used |
| `MaxRSS` | Peak resident memory usage (in KB) — the most useful memory metric |
| `MaxVMSize` | Peak virtual memory size |
| `CPUTime` | Total CPU time consumed across all cores |
| `TRESUsageInMax` | Max usage of tracked resources (CPUs, memory, GPUs) |

### Common `sacct` Queries

```bash
# Check a specific job (most useful fields)
sacct -j 12345 --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS

# All your jobs today
sacct -u $USER --starttime=$(date +%Y-%m-%d) \
  --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS

# Jobs from a date range
sacct -u $USER --starttime=2026-05-01 --endtime=2026-05-07 \
  --format=JobID,JobName,Partition,State,Elapsed,MaxRSS

# Only completed/failed jobs (skip running)
sacct -u $USER --state=COMPLETED,FAILED,TIMEOUT,OUT_OF_MEMORY \
  --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS

# Wide output (don't truncate fields)
sacct -j 12345 --format=JobID%20,JobName%30,State,ExitCode,Elapsed,MaxRSS --units=G
```

### Reading Exit Codes

| ExitCode | Meaning |
|---|---|
| `0:0` | Clean exit — job completed successfully |
| `1:0` | Script exited with error (check your program's output) |
| `0:9` | Killed by SIGKILL — usually out-of-memory |
| `0:15` | Killed by SIGTERM — job was cancelled or timed out |
| Non-zero signal | Job was terminated by the system; check `State` for reason |

If `State=OUT_OF_MEMORY`, increase your `--mem` or `--mem-per-cpu` directive.

---

## Job Efficiency — `jobstats`

Juno provides the `jobstats` tool, which produces a human-readable summary of CPU and memory utilization for a completed job. Load it with `module load jobstats` and run it after your job finishes.

```bash
$ module load jobstats
$ jobstats 189709

================================================================================
                          Slurm Job Statistics
================================================================================
         Job ID: 189709
   User/Account: utd000000/hpcre
       Job Name: test
          State: COMPLETED
          Nodes: 1
      CPU Cores: 20
     CPU Memory: 340GB (17GB per CPU-core)
  QOS/Partition: normal/normal
        Cluster: juno
     Start Time: Wed May 6, 2026 at 1:37 AM
       Run Time: 05:33:53
     Time Limit: 2-00:00:00

                            Overall Utilization
================================================================================
  CPU utilization  [|||||||||||||||||||||||||||||||||||||||||||||||96%]
  CPU memory usage [||||||||||||||||||||                           41%]

                            Detailed Utilization
================================================================================
  CPU utilization per node (CPU time used/run time)
      c-03-04: 4-11:08:12/4-15:17:40 (efficiency=96.3%)

  CPU memory usage per node - used/allocated
      c-03-04: 141.0GB/340GB (7.1GB/17GB per core of 20)

                                   Notes
================================================================================
  * This job only needed 12% of the requested time which was 2-00:00:00. For
    future jobs, please request less time by modifying the --time Slurm
    directive. This will lower your queue times and allow the Slurm job
    scheduler to work more effectively for all users.
```

**How to read the output:**

| Section | What to look for |
|---|---|
| **CPU utilization** | Should be close to 100% for CPU-bound jobs. If it's low (< 50%), you may be requesting more cores than your program can use |
| **CPU memory usage** | Shows what fraction of your requested memory was actually used. If this is low, reduce your `--mem` next time — over-requesting memory wastes resources and can increase queue times |
| **Run Time vs. Time Limit** | If you used only a small fraction of your requested time (like 12% in the example), request a shorter wall time in future jobs to improve queue priority |
| **Notes** | `jobstats` automatically flags inefficiencies and suggests improvements |

**Why this matters:** SLURM's fair-share system penalizes users who consistently over-request resources. Accurate requests get you back in the queue faster.

---

## Checking Job Priority — `sprio`

To understand why your job is waiting and how it ranks against others:

```bash
# Your jobs and their priority breakdown
sprio -u $USER

# All pending jobs, sorted by priority
sprio -l | sort -k3 -rn | head -20
```

The output shows how each priority component (fair share, age, job size) contributes to your job's total priority score. See the [SLURM scheduling page](slurm.md#slurm-scheduling-priorities) for how priority is calculated.

---

## Checking Your Fair Share — `sshare`

```bash
# Your current fair share
sshare -u $USER

# All users
sshare -a
```

A fair share value close to **1.0** means you have not used the cluster recently and will get high priority. After heavy usage, your share drops and recovers over ~two weeks.

---

## Estimating Queue Wait Time

For a pending job, ask SLURM when it expects the job to start:

```bash
squeue --me --start
```

The `START_TIME` column shows the estimated start time based on current cluster load. This is an estimate and can shift as other jobs finish or are submitted.

---

## Cancelling Jobs

```bash
# Cancel a specific job
scancel 12345

# Cancel all your jobs
scancel -u $USER

# Cancel only pending jobs
scancel -u $USER -t PENDING

# Cancel specific array tasks
scancel 12345_[3-7]

# Cancel jobs in a specific partition
scancel -u $USER -p normal
```

---

## Tips: Minimizing Wait Time and Getting Resources Faster

Your time in the queue is driven by two things: **how much you request** and your **fair-share score**. Requesting only what you actually need improves both — accurately-sized jobs are easier for the scheduler to fit (often via *backfill*, where a short job slots into a gap ahead of a larger one), and modest usage keeps your fair share high. The commands on this page let you check what's free and right-size each request.

### 1. Right-size your request

- **Memory (`--mem` / `--mem-per-cpu`)** — request enough, but not far more than you use. Over-requesting memory shrinks the set of nodes that can fit your job. Check a past job's peak usage with `MaxRSS` ([`sacct`](#job-accounting-sacct)) or [`jobstats`](#job-efficiency-jobstats), then set `--mem` a little above it.
- **Cores (`--ntasks` / `--cpus-per-task`)** — match the core count to what your program can actually use. If `jobstats` reports low CPU utilization, you're holding cores idle *and* waiting longer to get them. See [Nodes, Tasks, and CPUs](slurm.md#nodes-tasks-and-cpus).
- **Wall time (`--time`)** — request a realistic limit, not the 2-day maximum "just in case." Shorter jobs are eligible for backfill and start sooner; `jobstats` flags jobs that used only a fraction of their requested time.

### 2. Check what's free before you submit

- `sinfo -t idle,mix` — list nodes that can accept work right now (see [Checking Cluster Availability](#checking-cluster-availability-sinfo)).
- `scontrol show node <node>` — see exactly how many cores and how much memory a `mix` node still has free.
- `squeue --me --start` — ask SLURM for your pending job's estimated start time.

### 3. Widen where your job can run

- **Submit to multiple partitions** so the job starts wherever capacity frees up first: `sbatch -p normal,dev job.sh` (see [Submitting to Multiple Partitions](slurm.md#submitting-to-multiple-partitions)).
- **Use `dev` for short jobs** — it shares hardware with `normal` but is sized for quick turnaround (2-hour limit).
- **Right-size GPU requests** — a full H100 is in high demand, so a [virtual GPU slice](slurm.md#partitions-overview) (`a30-2.12gb`, `h100-2.47gb`) may start much sooner for light GPU work.

### 4. See the whole cluster at a glance — `cluster_monitor.py`

The per-command tools above are precise but narrow. For an at-a-glance picture of **where the free capacity is right now**, the community [`cluster_monitor.py`](../scripts/cluster_monitor.py) script renders a colour-coded CPU/memory utilization bar for every node, plus a one-line cluster summary. Lightly-loaded nodes (shown green) are where your job is most likely to start immediately.

[Download `cluster_monitor.py`](../scripts/cluster_monitor.py), save it on Juno, and run it on a login node (it only needs Python 3 and the standard SLURM commands):

```bash
python3 cluster_monitor.py             # one snapshot of all nodes
python3 cluster_monitor.py --watch     # refresh every 5s (Ctrl-C to stop)
python3 cluster_monitor.py --show-down # also show down/draining nodes
```

Example snapshot (in the terminal the bars are colour-coded — green = lightly loaded, yellow = busy, red = full):

```
========================================================================================================================
SLURM CLUSTER - 2026-06-17 00:06:09
Nodes: 126 (30 idle, 22 mixed, 66 alloc, 7 down) | CPUs: 5169/8576 (60%) | GPUs: 0 | Jobs: 72
========================================================================================================================

Node         St    CPU                Mem                  Node         St    CPU                Mem
------------ ----- ------------------ ------------------   ------------ ----- ------------------ ------------------
c-01-12      mixed [█████░░░░░]   50%  [████░░░░░░]   43%    c-04-16      mixed [██░░░░░░░░]   25%  [████░░░░░░]   46%
c-02-01      mixed [██░░░░░░░░]   25%  [███████░░░]   80%    c-04-17      mixed [██░░░░░░░░]   25%  [██░░░░░░░░]   25%
c-02-13      mixed [██░░░░░░░░]   25%  [████░░░░░░]   50%    g-01-01      mixed [███░░░░░░░]   38%  [██░░░░░░░░]   24%
c-03-06      mixed [█████░░░░░]   50%  [████░░░░░░]   48%    g-03-01      mixed [█░░░░░░░░░]   11%  [█░░░░░░░░░]   18%
c-03-09      mixed [█████░░░░░]   50%  [██████░░░░]   60%    g-05-01      mixed [███████░░░]   77%  [████░░░░░░]   46%
...
(output continues for every node; idle and mixed nodes are where jobs start soonest)
========================================================================================================================
```

!!! tip
    Combine the script with the strategies above: find a green/`mix` node with free cores and memory, then submit a request that fits within what that node (or partition) has available. Pair it with `--watch` during busy periods to grab capacity the moment it frees up.

## Quick Reference

| Command | Purpose |
|---|---|
| `cluster_monitor.py` | At-a-glance CPU/memory utilization for every node ([download](../scripts/cluster_monitor.py)) |
| `sinfo` | Cluster-wide node/partition availability |
| `sinfo -t idle,mix` | Show only nodes with free capacity |
| `squeue --me` | Your running and pending jobs |
| `squeue --me --start` | Estimated start time for pending jobs |
| `scontrol show job <id>` | Full details of a job (running or pending) |
| `scontrol show node <node>` | Hardware and allocation details for a node |
| `scontrol show partition <name>` | Configuration and limits for a partition |
| `scontrol update JobId=<id> ...` | Modify a pending job |
| `sacct -j <id> --format=...` | Accounting data for completed jobs (exit code, memory, elapsed time) |
| `jobstats <id>` | CPU and memory efficiency report (requires `module load jobstats`) |
| `sprio -u $USER` | Priority breakdown for your pending jobs |
| `sshare -u $USER` | Your current fair-share score |
| `scancel <id>` | Cancel a job |

---

## Related Pages

- [SLURM Job Scheduler](slurm.md) — writing job scripts, submitting jobs, partitions overview
- [Common Scientific Programs](common-programs.md) — ready-to-use job script examples
- [Launcher](launcher.md) — running many small tasks efficiently
