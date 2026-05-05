# Scratch Space

## What is Scratch Space?

Scratch space is a high-performance temporary storage system designed for active computational workloads on HPC clusters. It provides fast I/O for large datasets during job execution.

## Key Characteristics

### High Performance
- **Parallel filesystem**: Optimized for multiple simultaneous read/write operations
- **High bandwidth**: Up to **10× faster** than the IO2 storage system (`~`, `~/work`, `/groups`) for large I/O
- **Large I/O capacity**: Handles big data operations efficiently

### Temporary Storage
- **Not backed up**: No backups exist of scratch data
- **Automatic purge**: Files may be deleted after 45 days of inactivity
- **Volatile**: Never rely on scratch for permanent storage

### Large Capacity
- **Generous quota**: 30 TB per user
- **Shared resource**: All users contribute to overall capacity
- **Fair usage expected**: Clean up regularly

## Location and Access

### Path

```bash
# Your scratch directory
~/scratch

```

### Navigate to Scratch

```bash
# Go to your scratch space
cd ~/scratch

```

### Check Usage

```bash
# Your scratch usage
du -sh ~/scratch

# Detailed breakdown
du -h --max-depth=1 ~/scratch | sort -h
```

## When to Use Scratch

### Appropriate Uses

**Large input/output files**:
```bash
# Store large datasets during active computation
~/scratch/project/input_data.csv
```

**Intermediate results**:
```bash
# Temporary files generated during analysis
~/scratch/simulation/temp_output_*.dat
```

**High I/O workloads**:
- Processing large datasets
- Writing many small files
- Frequent read/write operations
- Parallel I/O from multiple nodes

**Working directories for jobs**:
```bash
#!/bin/bash
#SBATCH -J analysis
#SBATCH -o output_%j.log

WORK_DIR=~/scratch/job_$SLURM_JOB_ID
mkdir -p $WORK_DIR
cd $WORK_DIR

# Run computation
python analyze.py
```

### Inappropriate Uses

**Long-term storage**: 
- Data you need after project completes
- Results for publication
- Reference datasets

**Irreplaceable data**:
- Original data without backup
- Unique experimental results
- Data that can't be regenerated

**Small files**:
- Source code (use home directory)
- Scripts and configuration files
- Small reference files

**Archival purposes**:
- Completed project data
- Historical records
- Backup copies

## Purge Policy

### Automatic Purge Rules

**Scratch policy**:
- Files not accessed in **[45 days]** may be purged
- System checks **access time** (last read or write)
- Purge runs automatically on schedule
- **No recovery possible** after purge

### What Triggers Purge?

**Based on access time**:
```bash
# Check last access time
stat ~/scratch/myfile.txt
```

**Not purged if you**:
- Read the file
- Write to the file
- Run programs that access it
- Copy it (as destination)

**Still purged if you only**:
- Look at directory listing
- Check file properties
- Navigate through directories

### Prevent Purge

**Option 1: Touch files** (updates access time):
```bash
# Update access time on single file
touch ~/scratch/important_file.txt

# Update all files in directory
find ~/scratch/project -type f -exec touch {} \;
```

**Option 2: Move to home or work directories** (permanent storage):
```bash
# Move important results
mv ~/scratch/results/*.txt $HOME/project/results/
```

**Option 3: Archive externally**:
```bash
# Backup to external storage
rsync -avzP ~/scratch/data/ user@external-server:/backup/
```

### Check Purge Eligibility

Find files at risk:
```bash
# Files not accessed in 30 days
find ~/scratch -type f -atime +30

# Count files at risk
find ~/scratch -type f -atime +30 | wc -l

# Total size of at-risk files
find ~/scratch -type f -atime +30 -exec du -ch {} + | tail -1
```

## Best Practices

### 1. Clean Up Regularly

**After each job completion**:
```bash
#!/bin/bash
#SBATCH -J my_job

# Your computation here
python simulate.py

# Copy results to home
cp important_results.txt $HOME/results/

# Clean up scratch
rm -rf ~/scratch/job_$SLURM_JOB_ID
```

**Regular maintenance**:
```bash
# Monthly cleanup script
#!/bin/bash
# Remove old temporary files
find ~/scratch -name "*.tmp" -mtime +7 -delete

# Remove old log files
find ~/scratch -name "*.log" -mtime +30 -delete

# Archive important data
rsync -avzP ~/scratchcompleted_projects/ $HOME/archive/
rm -rf ~/scratchcompleted_projects/
```

### 2. Organize Your Scratch

**Recommended structure**:
```
~/scratch
├── project1/
│   ├── input/          # Input datasets
│   ├── output/         # Output results
│   ├── tmp/            # Temporary files
│   └── logs/           # Job logs
├── project2/
│   └── ...
└── shared/             # Shared with group members
```

### 3. Use Job-Specific Directories

```bash
#!/bin/bash
#SBATCH -J simulation

# Create unique directory for this job
JOB_DIR=~/scratch/sim_$SLURM_JOB_ID
mkdir -p $JOB_DIR
cd $JOB_DIR

# Run computation
./simulation > output.log

# Copy results to permanent storage
cp output.log $HOME/results/simulation_$SLURM_JOB_ID.log

# Clean up
cd ~/scratch
rm -rf $JOB_DIR
```

### 4. Monitor Usage

**Regular checks**:
```bash
# Check total usage
du -sh ~/scratch

# Check by project
du -sh ~/scratch/*/

# Find largest files
find ~/scratch -type f -exec du -h {} + | sort -hr | head -20
```

**Set up monitoring**:
```bash
# Add to crontab (runs weekly)
0 0 * * 0 du -sh ~/scratch >> $HOME/scratch_usage.log
```

## Workflow Best Practices

### 1. Stage Data Workflow

```bash
# Before job starts: Copy to scratch
scp large_dataset.tar.gz username@juno.utdallas.edu:~/scratch
ssh username@juno.utdallas.edu
cd ~/scratch
tar xzf large_dataset.tar.gz
```

### 2. Process on Scratch

```bash
#!/bin/bash
#SBATCH -J process_data

INPUT=~/scratch/large_dataset/
OUTPUT=~/scratch/results/

mkdir -p $OUTPUT
python process.py --input $INPUT --output $OUTPUT
```

### 3. Save Results

```bash
# After job completes: Copy important results to home
cp ~/scratch/results/summary.txt $HOME/project/
cp ~/scratch/results/figures/*.png $HOME/project/figures/

# Or archive externally
rsync -avzP ~/scratch/results/ user@backup-server:/archive/
```

### 4. Clean Up Scratch

```bash
# Remove large temporary files
rm -rf ~/scratch/large_dataset/
rm -rf ~/scratch/results/

# Keep only what you need
```

## Scratch vs Home Directory

| Aspect | Scratch | Home |
|--------|---------|------|
| **Purpose** | Active computation | Code, scripts, small data |
| **Size** | Large (TBs) | Small (GBs) |
| **Backup** | No | Yes |
| **Retention** | Temporary (purged) | Permanent |
| **Performance** | High I/O | Standard |
| **Use for** | Big data processing | Source code, configs |

## Common Patterns

### Pattern 1: Checkpoint to Home

```bash
#!/bin/bash
#SBATCH -J long_simulation

WORK=~/scratch/simulation
HOME_BACKUP=$HOME/simulation_checkpoints

mkdir -p $WORK $HOME_BACKUP

cd $WORK

# Run simulation with periodic checkpoints
for i in {1..100}; do
    python step_$i.py
    
    # Checkpoint every 10 steps
    if [ $((i % 10)) -eq 0 ]; then
        cp checkpoint_$i.dat $HOME_BACKUP/
    fi
done
```

### Pattern 2: Array Jobs with Scratch

```bash
#!/bin/bash
#SBATCH -J array_job
#SBATCH --array=1-100

# Each task gets unique scratch directory
TASK_DIR=~/scratch/task_$SLURM_ARRAY_TASK_ID
mkdir -p $TASK_DIR
cd $TASK_DIR

# Process this task's data
python process.py --task $SLURM_ARRAY_TASK_ID

# Save results
cp output.txt $HOME/results/output_$SLURM_ARRAY_TASK_ID.txt

# Clean up
rm -rf $TASK_DIR
```

### Pattern 3: Node-Local Temp + Scratch

```bash
#!/bin/bash
#SBATCH -J hybrid_storage

# Use node-local for very fast temporary I/O
TEMP_DIR=$TMPDIR/workdir
mkdir -p $TEMP_DIR

# Copy input from scratch to node-local
cp ~/scratch/input/* $TEMP_DIR/

# Process with fast local I/O
cd $TEMP_DIR
python fast_process.py

# Copy results back to scratch
cp output/* ~/scratch/results/

# Later, move from scratch to home
```

## Troubleshooting

### Files Disappeared

**If files were purged**:
1. Check access times were too old
2. Files are **not recoverable**
3. Check backups on external storage
4. Regenerate data if possible

**Prevention**:
- Regular backups
- Monitor age of files
- Touch files to update access time
- Move important data to home

### Out of Scratch Space

**Check usage**:
```bash
du -sh ~/scratch
```

**Solutions**:
1. **Delete old files**:
   ```bash
   find ~/scratch -mtime +30 -delete
   ```

2. **Compress large files**:
   ```bash
   gzip ~/scratch/large_file.txt
   ```

3. **Archive to external storage**:
   ```bash
   rsync -avzP ~/scratch/old_project/ user@backup:/archive/
   rm -rf ~/scratch/old_project/
   ```

4. **Request quota increase** (if needed for active work)

### Slow I/O on Scratch

**Possible causes**:
- Many small files (use fewer large files)
- Many users accessing simultaneously
- Filesystem contention

**Solutions**:
- Combine small files into larger archives
- Use node-local $TMPDIR for temporary I/O
- Schedule jobs during off-peak hours
- Use parallel I/O libraries

## Automated Cleanup Script

**Create cleanup script** (`~/bin/clean_scratch.sh`):
```bash
#!/bin/bash
# Automated scratch cleanup script

SCRATCH_DIR=~/scratch
LOG_FILE=$HOME/scratch_cleanup.log
DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo "[$DATE] Starting scratch cleanup" >> $LOG_FILE

# Remove temporary files older than 7 days
TEMP_COUNT=$(find $SCRATCH_DIR -name "*.tmp" -mtime +7 -delete -print | wc -l)
echo "[$DATE] Removed $TEMP_COUNT temp files" >> $LOG_FILE

# Remove log files older than 30 days
LOG_COUNT=$(find $SCRATCH_DIR -name "*.log" -mtime +30 -delete -print | wc -l)
echo "[$DATE] Removed $LOG_COUNT log files" >> $LOG_FILE

# Report old files (not deleted, just listed)
OLD_FILES=$(find $SCRATCH_DIR -type f -atime +45 | wc -l)
echo "[$DATE] Found $OLD_FILES files not accessed in 45+ days" >> $LOG_FILE

echo "[$DATE] Cleanup complete" >> $LOG_FILE
```

**Schedule with cron**:
```bash
# Edit crontab
crontab -e

# Add line (runs weekly on Sunday at 2 AM)
0 2 * * 0 $HOME/bin/clean_scratch.sh
```

## Quick Reference

### Essential Commands

```bash
# Navigate to scratch
cd ~/scratch

# Check usage
du -sh ~/scratch

# Find old files
find ~/scratch -atime +30

# Update access times
find ~/scratch/important -type f -exec touch {} \;

# Clean up
rm -rf ~/scratch/old_project

# Copy to permanent storage
cp -r ~/scratch/results $HOME/
```

### Recommended Workflow

1. **Copy** data to scratch before job
2. **Process** data on scratch during job  
3. **Save** important results to home
4. **Clean** up scratch after job
5. **Archive** completed work externally

## Next Steps

- [Learn about data transfer methods →](storage.md)
- [Submit jobs that use scratch space →](../running-programs/slurm.md)
- [Optimize I/O performance →](../advanced/python-optimization.md)

## Need Help?

- **Scratch space questions**: [CircAssist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Purge policy details**: Check HPC website or ask support
- **Quota increase**: Open ticket with justification