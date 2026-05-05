# High Throughput Processing with Launcher

## What is Launcher?

Launcher is a utility for executing multiple serial or small parallel tasks simultaneously on HPC clusters. It's designed for high-throughput computing where you have many independent jobs to run.

## When to Use Launcher

### Ideal Use Cases

✓ **Parameter sweeps**: Running same code with different parameters  
✓ **Data processing**: Processing many independent files  
✓ **Monte Carlo simulations**: Many independent runs  
✓ **Bioinformatics pipelines**: Processing multiple samples  
✓ **Machine learning**: Hyperparameter tuning, cross-validation  
✓ **Ensemble simulations**: Multiple independent simulations  

### Not Suitable For

✗ Single large parallel job  
✗ Jobs requiring inter-communication  
✗ Tasks with dependencies (use workflow managers instead)  
✗ Very short jobs (<1 minute each)  

## Launcher vs Alternatives

| Method | Best For | Advantages | Disadvantages |
|--------|----------|------------|---------------|
| **Launcher** | Many independent tasks | Simple, automatic load balancing | Limited dependency handling |
| **Array Jobs** | Identical tasks, indexed | Native SLURM, simple | Harder to mix different commands |
| **GNU Parallel** | Shell-level parallelism | Very flexible | More complex syntax |
| **Workflow Tools** | Complex dependencies | DAG support, robust | Steep learning curve |

## Basic Launcher Usage

### Load module

Launcher is available as a module on Juno:

```bash
module load launcher
```


### Create Task List

Create a file with one command per line (e.g., `tasks.txt`):

```bash
python process.py data1.csv output1.txt
python process.py data2.csv output2.txt
python process.py data3.csv output3.txt
python process.py data4.csv output4.txt
```

### Basic Job Script

```bash
#!/bin/bash
#SBATCH --job-name=launcher_job
#SBATCH --output=launcher_%j.out
#SBATCH --error=launcher_%j.err
#SBATCH --partition=normal
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=64
#SBATCH --time=00:30:00

# Load modules
module load launcher

# Set launcher variables
export LAUNCHER_WORKDIR=$PWD
export LAUNCHER_JOB_FILE=$PWD/tasks.txt
export LAUNCHER_PPN=64      # tasks per node
export LAUNCHER_NHOSTS=2

echo "Starting tasks..."
$LAUNCHER_DIR/paramrun
echo "All tasks completed."
```

**How it works**:
- Launcher reads `tasks.txt`
- Distributes tasks across all allocated cores (2 nodes × 64 cores = 128 cores)
- Runs tasks until all complete
- Automatic load balancing

## Advanced Usage

### Parametric Job Example

**Generate tasks programmatically**:

```python
# generate_tasks.py
import numpy as np

with open('tasks.txt', 'w') as f:
    for alpha in np.linspace(0.1, 1.0, 10):
        for beta in np.linspace(0.1, 1.0, 10):
            f.write(f"python simulate.py --alpha {alpha} --beta {beta}\n")
```

**Job script**:
```bash
#!/bin/bash
#SBATCH -J param_sweep
#SBATCH -o output_%j.log
#SBATCH -N 2
#SBATCH -n 32
#SBATCH -t 4:00:00

module load launcher

# Generate task list
python generate_tasks.py

# Run launcher
export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun
```

### Multi-Node Jobs

**Using multiple nodes**:

```bash
#!/bin/bash
#SBATCH -J multinode_launcher
#SBATCH -N 4                    # 4 nodes
#SBATCH -n 64                   # 64 total cores
#SBATCH -t 8:00:00

module load launcher

export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD

# Launcher automatically uses all allocated cores
$LAUNCHER_DIR/paramrun
```

### Launcher Environment Variables

```bash
# Required
export LAUNCHER_JOB_FILE=tasks.txt      # Task list file
export LAUNCHER_WORKDIR=$PWD            # Working directory

# Optional — explicit multi-node control
export LAUNCHER_PPN=64                  # Tasks per node (tasks per node)
export LAUNCHER_NHOSTS=2               # Number of nodes allocated

# Other optional
export LAUNCHER_NPHI=0                  # Hyperthreads per core (usually 0)
export LAUNCHER_BIND=1                  # Bind tasks to cores
```

`LAUNCHER_PPN` and `LAUNCHER_NHOSTS` are useful when you want explicit control over how tasks are distributed across nodes. If omitted, Launcher infers them from the SLURM allocation.

## Task File Formats

### Simple Commands

```bash
# tasks.txt
./program input1.dat
./program input2.dat
./program input3.dat
```

### With Arguments

```bash
python script.py --input file1.csv --output result1.txt
python script.py --input file2.csv --output result2.txt
Rscript analysis.R data1.txt
Rscript analysis.R data2.txt
```

### Mixed Commands

```bash
python preprocess.py file1.dat
./simulation file1_processed.dat
python postprocess.py file1_results.dat
python preprocess.py file2.dat
./simulation file2_processed.dat
python postprocess.py file2_results.dat
```

### With Module Loading

```bash
module load matlab; matlab -nodisplay -r "run('script1.m'); exit"
module load matlab; matlab -nodisplay -r "run('script2.m'); exit"
```

## Practical Examples

### Example 1: Data Processing

**Scenario**: Process 1000 CSV files

```python
# generate_tasks.py
import glob

with open('tasks.txt', 'w') as f:
    for csv_file in glob.glob('data/*.csv'):
        output = csv_file.replace('data/', 'results/').replace('.csv', '_result.txt')
        f.write(f"python analyze.py {csv_file} {output}\n")
```

```bash
#!/bin/bash
#SBATCH -J data_processing
#SBATCH -N 2
#SBATCH -n 32
#SBATCH -t 4:00:00

module load launcher

# Generate tasks
mkdir -p results
python generate_tasks.py

# Run
export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun
```

### Example 2: Parameter Sweep

**Scenario**: Test different hyperparameters

```bash
#!/bin/bash
#SBATCH -J hyperparam_search
#SBATCH -N 1
#SBATCH -n 16
#SBATCH -t 6:00:00

module load launcher

# Generate parameter combinations
python << 'EOF'
import itertools

learning_rates = [0.001, 0.01, 0.1]
batch_sizes = [16, 32, 64]
hidden_sizes = [64, 128, 256]

with open('tasks.txt', 'w') as f:
    for lr, bs, hs in itertools.product(learning_rates, batch_sizes, hidden_sizes):
        f.write(f"python train.py --lr {lr} --batch {bs} --hidden {hs}\n")
EOF

# Run launcher
export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun
```

### Example 3: Bioinformatics Pipeline

**Scenario**: Process multiple genomic samples

```bash
# tasks.txt
module load blast; blastp -query sample1.fasta -db nr -out sample1.blast
module load blast; blastp -query sample2.fasta -db nr -out sample2.blast
module load bowtie2; bowtie2 -x genome -U sample1.fastq -S sample1.sam
module load bowtie2; bowtie2 -x genome -U sample2.fastq -S sample2.sam
module load samtools; samtools view -bS sample1.sam > sample1.bam
module load samtools; samtools view -bS sample2.sam > sample2.bam
```

```bash
#!/bin/bash
#SBATCH -J bio_pipeline
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=64GB
#SBATCH -t 12:00:00

module load launcher

export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun
```

### Example 4: Image Processing

**Scenario**: Process thousands of images

```python
# generate_image_tasks.py
import os
import glob

with open('tasks.txt', 'w') as f:
    for img in glob.glob('images/*.jpg'):
        basename = os.path.basename(img)
        f.write(f"python process_image.py {img} processed/{basename}\n")
```

```bash
#!/bin/bash
#SBATCH -J image_processing
#SBATCH -N 1
#SBATCH -n 20
#SBATCH -t 3:00:00

module load launcher

mkdir -p processed
python generate_image_tasks.py

export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun
```

## Monitoring and Debugging

### Track Progress

Launcher creates log files:

```bash
# Check main log
tail -f launcher_JOBID.log

# Count completed tasks
grep -c "TACC: Launcher: Task" launcher_JOBID.log
```

### Individual Task Logs

**Redirect task output**:

```bash
# In tasks.txt
python script.py arg1 > logs/task1.out 2> logs/task1.err
python script.py arg2 > logs/task2.out 2> logs/task2.err
```

### Failed Tasks

**Identify failures**:

```bash
# Check for errors
grep -i error launcher_*.log

# Find non-zero exit codes
grep "TACC: Launcher: Task.*returned" launcher_*.log
```

**Rerun failed tasks**:

```python
# extract_failed.py
import re

with open('launcher_12345.log', 'r') as f:
    content = f.read()

# Find failed tasks
failed = re.findall(r'Task (\d+).*returned (\d+)', content)
failed = [int(task) for task, code in failed if int(code) != 0]

# Read original tasks
with open('tasks.txt', 'r') as f:
    tasks = f.readlines()

# Write failed tasks to new file
with open('retry_tasks.txt', 'w') as f:
    for i in failed:
        f.write(tasks[i])
```

## Performance Optimization

### Task Granularity

**Too short** (< 1 minute):
- High overhead
- Poor efficiency

**Too long** (> 1 hour):
- Load imbalance
- Wasted resources if job fails

**Optimal**: 5-30 minutes per task

### Resource Allocation

**Match cores to tasks**:

```bash
# Bad: More cores than tasks
#SBATCH -n 64
# tasks.txt has only 10 tasks

# Good: Cores ≈ number of concurrent tasks
#SBATCH -n 10
```

**Memory per task**:

```bash
# If each task needs 4GB and node has 128GB
#SBATCH -n 32          # 128GB / 4GB = 32 tasks
#SBATCH --mem=128GB
```

### I/O Considerations

**Use scratch space**:

```bash
# Copy data to scratch first
cp -r data/ ~/scratch/job_$SLURM_JOB_ID/
cd ~/scratch/job_$SLURM_JOB_ID/

# Run launcher
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun

# Copy results back
cp -r results/ $SLURM_SUBMIT_DIR/
```

**Avoid simultaneous writes to same file**:

```bash
# Bad: All tasks write to same log
python task.py >> shared.log

# Good: Separate logs
python task.py > logs/task_$ID.log
```

## Alternative Tools

### SLURM Array Jobs

**For indexed tasks**:

```bash
#!/bin/bash
#SBATCH --array=1-100
#SBATCH -n 1

python process.py input_${SLURM_ARRAY_TASK_ID}.dat
```

**Pros**: Native SLURM, simpler for indexed tasks  
**Cons**: Less flexible than Launcher

### GNU Parallel

**Shell-level parallelism**:

```bash
module load parallel

# Run commands in parallel
parallel -j 16 < tasks.txt

# Or
cat input_files.txt | parallel -j 16 python process.py {}
```

**Pros**: Very flexible, powerful  
**Cons**: Single-node only, complex syntax

### Comparison

**Choose Launcher when**:
- Multi-node capability needed
- Simple task list preferred
- Automatic load balancing desired

**Choose Array Jobs when**:
- Tasks are indexed/numbered
- Simple pattern (same command, different input)
- Native SLURM features needed

**Choose GNU Parallel when**:
- Single-node sufficient
- Need shell features (pipes, etc.)
- Complex command construction

## Best Practices

### 1. Test Before Scaling

```bash
# Test with small subset first
head -10 tasks.txt > test_tasks.txt

# Run test job
#SBATCH -n 4
#SBATCH -t 0:30:00
export LAUNCHER_JOB_FILE=test_tasks.txt
```

### 2. Organize Output

```bash
# Create organized output structure
mkdir -p logs results checkpoints

# In tasks.txt
python run.py input1.dat > logs/task1.log 2>&1
python run.py input2.dat > logs/task2.log 2>&1
```

### 3. Handle Failures Gracefully

```bash
# Make tasks idempotent (safe to rerun)
if [ ! -f output.txt ]; then
    python process.py input.txt output.txt
fi
```

### 4. Clean Up

```bash
# After successful completion
cd ~/scratch
rm -rf job_$SLURM_JOB_ID
```

### 5. Document Your Workflow

```bash
# Add comments to task file
# Parameter sweep: learning rates
python train.py --lr 0.001
python train.py --lr 0.01
# Parameter sweep: batch sizes
python train.py --batch 16
python train.py --batch 32
```

## Troubleshooting

### Tasks Not Running

**Check**:
```bash
# Verify task file exists
ls -l tasks.txt

# Check launcher loaded
module list | grep launcher

# Verify environment variables
echo $LAUNCHER_JOB_FILE
echo $LAUNCHER_WORKDIR
```

### Slow Performance

**Possible causes**:
- Tasks too short (overhead dominates)
- I/O bottleneck (all tasks accessing same files)
- Insufficient resources (not enough cores)

**Solutions**:
- Batch multiple small tasks together
- Use scratch space for I/O
- Increase core count

### Uneven Load

**Some cores finish early**:
- Tasks have variable runtime
- Expected behavior
- Launcher handles automatically

**If severe**:
- Break long tasks into smaller pieces
- Sort tasks by expected runtime

## Example Workflows

### Complete Parameter Sweep Workflow

```bash
#!/bin/bash
# run_sweep.sh

# 1. Generate parameter combinations
python << 'EOF'
import numpy as np

params = []
for alpha in np.linspace(0.1, 1.0, 10):
    for beta in np.linspace(0.1, 1.0, 10):
        for gamma in [0.001, 0.01, 0.1]:
            params.append((alpha, beta, gamma))

with open('tasks.txt', 'w') as f:
    for i, (a, b, g) in enumerate(params):
        f.write(f"python simulate.py --alpha {a} --beta {b} --gamma {g} --output results/run_{i}.txt\n")

print(f"Generated {len(params)} tasks")
EOF

# 2. Submit launcher job
sbatch << 'EOSLURM'
#!/bin/bash
#SBATCH -J param_sweep
#SBATCH -N 2
#SBATCH -n 48
#SBATCH -t 8:00:00
#SBATCH -o sweep_%j.log

module load launcher

mkdir -p results

export LAUNCHER_JOB_FILE=tasks.txt
export LAUNCHER_WORKDIR=$PWD
$LAUNCHER_DIR/paramrun
EOSLURM
```

## Next Steps

- [Learn about parallelism models →](parallelism.md)
- [Optimize Python code →](../advanced/python-optimization.md)
- [Use containers for reproducibility →](../advanced/containers.md)

## Need Help?

- **Launcher installation**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Workflow design**: Request consultation via support ticket
- **Performance issues**: Include job ID and task file in ticket