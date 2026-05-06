# Linux Commands Crash Course

## Introduction

This guide covers essential Linux commands for working on Juno. While not comprehensive, it provides the minimum knowledge needed to navigate and work effectively on the HPC cluster.

For deeper Linux knowledge, consider:

- Online tutorials: [linuxcommand.org](https://linuxcommand.org)
- Books: "The Linux Command Line" by William Shotts
- Man pages: `man command_name`

## Getting Help

### Man Pages (Manual Pages)

```bash
# View manual for a command
man ls
man cp

# Search man pages
man -k search_term

# Short description
whatis ls
```

### Built-in Help

```bash
# Most commands have --help option
ls --help
cp --help
```

## Navigation

### Basic Navigation Commands

```bash
# Print working directory (where am I?)
pwd

# List files and directories
ls                    # Basic listing
ls -l                # Long format (detailed)
ls -a                # Show hidden files (starting with .)
ls -lh               # Human-readable sizes
ls -lt               # Sort by modification time
ls -ltr              # Sort by time, reverse (oldest first)

# Change directory
cd /scratch/$USER    # Go to specific path
cd ~                 # Go to home directory
cd -                 # Go to previous directory
cd ..                # Go up one level
cd ../..             # Go up two levels
```

### Paths

**Absolute paths** start from root:
```bash
cd /home/username/project
```

**Relative paths** start from current location:
```bash
cd project          # Go to project/ in current directory
cd ../other         # Go up one level, then to other/
```

**Special directories**:

- `.` = current directory
- `..` = parent directory
- `~` = home directory
- `/` = root directory

## File Operations

### Creating Files and Directories

```bash
# Create empty file
touch filename.txt

# Create directory
mkdir dirname

# Create nested directories
mkdir -p path/to/nested/directory

# Create multiple directories
mkdir dir1 dir2 dir3
```

### Copying Files

```bash
# Copy file
cp source.txt destination.txt

# Copy file to directory
cp file.txt /scratch/$USER/

# Copy directory recursively
cp -r source_dir/ destination_dir/

# Copy and preserve attributes
cp -p file.txt backup.txt

# Copy multiple files to directory
cp file1.txt file2.txt file3.txt /destination/
```

### Moving and Renaming

```bash
# Rename file (move within same directory)
mv oldname.txt newname.txt

# Move file to different directory
mv file.txt /scratch/$USER/

# Move directory
mv source_dir/ /new/location/

# Move multiple files
mv file1.txt file2.txt /destination/
```

### Deleting Files

!!! danger
    Deleted files cannot be recovered. Be careful with `rm` command!

```bash
# Remove file
rm file.txt

# Remove multiple files
rm file1.txt file2.txt

# Remove directory and contents
rm -r directory/

# Force remove (no confirmation)
rm -f file.txt

# Remove with confirmation
rm -i file.txt

# Remove empty directory
rmdir empty_dir/
```

### Wildcards

```bash
# * matches any characters
ls *.txt             # All .txt files
rm output_*.log      # All files starting with output_ ending in .log

# ? matches single character
ls file?.txt         # file1.txt, fileA.txt, etc.

# [] matches character range
ls file[1-3].txt     # file1.txt, file2.txt, file3.txt
ls [A-Z]*.txt        # Files starting with uppercase letter
```

## Viewing Files

### Display File Contents

```bash
# Display entire file
cat filename.txt

# Display with line numbers
cat -n filename.txt

# Display multiple files
cat file1.txt file2.txt

# View file page by page
less filename.txt    # Use space to scroll, q to quit
more filename.txt    # Similar to less

# Display first lines
head filename.txt        # First 10 lines
head -n 20 filename.txt  # First 20 lines

# Display last lines
tail filename.txt        # Last 10 lines
tail -n 20 filename.txt  # Last 20 lines
tail -f logfile.log      # Follow file (useful for logs)
```

### Searching in Files

```bash
# Search for pattern in file
grep "pattern" filename.txt

# Case-insensitive search
grep -i "pattern" filename.txt

# Show line numbers
grep -n "pattern" filename.txt

# Search recursively in directory
grep -r "pattern" directory/

# Search for whole word
grep -w "word" filename.txt

# Show lines NOT matching pattern
grep -v "pattern" filename.txt

# Count matches
grep -c "pattern" filename.txt
```

## File Information

### File Details

```bash
# Detailed file information
ls -lh filename.txt

# File type
file filename.txt

# Disk usage
du -h filename.txt           # File size
du -sh directory/            # Directory total size
du -h --max-depth=1          # Size of subdirectories

# Count lines, words, characters
wc filename.txt              # All three
wc -l filename.txt           # Lines only
wc -w filename.txt           # Words only
```

### File Permissions

**Understanding permissions**:
```
-rwxr-xr--
│││││││││└─ Others can read
││││││││└── Others cannot write
│││││││└─── Others cannot execute
││││││└──── Group can read
│││││└───── Group cannot write
││││└────── Group can execute
│││└─────── Owner can read
││└──────── Owner can write
│└───────── Owner can execute
└────────── File type (- = file, d = directory)
```

**Changing permissions**:
```bash
# Make file executable
chmod +x script.sh

# Remove write permission
chmod -w file.txt

# Set specific permissions (rwxr-xr-x)
chmod 755 file.txt

# Owner: read+write, Group: read, Others: nothing
chmod 640 file.txt

# Recursive permission change
chmod -R 755 directory/
```

**Common permission codes**:

- `644`: Standard file (rw-r--r--)
- `755`: Executable file or directory (rwxr-xr-x)
- `700`: Private file/directory (rwx------)
- `600`: Private file (rw-------)

**Changing ownership**:
```bash
# Change owner (usually requires sudo)
chown newowner file.txt

# Change group
chgrp newgroup file.txt

# Change both
chown newowner:newgroup file.txt
```

## Text Editing

### Nano (Beginner-Friendly)

```bash
# Open file
nano filename.txt

# Common commands (shown at bottom):
# Ctrl+O: Save
# Ctrl+X: Exit
# Ctrl+K: Cut line
# Ctrl+U: Paste
# Ctrl+W: Search
```

### Vim (Powerful, Steeper Learning Curve)

```bash
# Open file
vim filename.txt

# Basic vim commands:
# i: Enter insert mode
# Esc: Return to command mode
# :w: Save
# :q: Quit
# :wq: Save and quit
# :q!: Quit without saving
# dd: Delete line
# yy: Copy line
# p: Paste
# /pattern: Search
```

### Quick Edits

```bash
# Append to file
echo "new line" >> file.txt

# Overwrite file
echo "new content" > file.txt

# Edit in place with sed
sed -i 's/old/new/g' file.txt
```

## Process Management

### Viewing Processes

```bash
# List your processes
ps

# Detailed process list
ps aux

# Your processes
ps -u $USER

# Tree view
ps -ef --forest

# Monitor processes (refreshing)
top              # Press q to quit
htop             # More user-friendly (if available)
```

### Controlling Processes

```bash
# Run in background
command &

# Send running process to background
# Ctrl+Z (suspend), then:
bg

# Bring to foreground
fg

# List background jobs
jobs

# Kill process by PID
kill 12345

# Force kill
kill -9 12345

# Kill by name
pkill process_name
killall process_name
```

## Redirection and Pipes

### Output Redirection

```bash
# Save output to file (overwrite)
ls -l > filelist.txt

# Append output to file
ls -l >> filelist.txt

# Redirect error messages
command 2> errors.txt

# Redirect both output and errors
command > output.txt 2>&1
```

### Pipes

```bash
# Send output of one command to another
ls -l | grep ".txt"

# Chain multiple commands
cat file.txt | grep "pattern" | sort | uniq

# Count files
ls | wc -l

# Find large files
du -h | sort -h | tail -10
```

## Compression and Archives

### tar Archives

```bash
# Create tar archive
tar -cf archive.tar directory/

# Create compressed tar.gz
tar -czf archive.tar.gz directory/

# Create compressed tar.bz2
tar -cjf archive.tar.bz2 directory/

# Extract tar archive
tar -xf archive.tar

# Extract tar.gz
tar -xzf archive.tar.gz

# Extract tar.bz2
tar -xjf archive.tar.bz2

# List contents
tar -tzf archive.tar.gz

# Extract to specific directory
tar -xzf archive.tar.gz -C /destination/
```

### Compression

```bash
# Compress with gzip
gzip file.txt              # Creates file.txt.gz

# Decompress
gunzip file.txt.gz

# Keep original
gzip -k file.txt

# Compress with bzip2 (better compression)
bzip2 file.txt             # Creates file.txt.bz2
bunzip2 file.txt.bz2

# zip/unzip
zip archive.zip file1 file2
zip -r archive.zip directory/
unzip archive.zip
```

## Network and File Transfer

### Network Commands

```bash
# Check connectivity
ping hostname

# Trace route
traceroute hostname

# Check network statistics
netstat

# Download files
wget URL
curl -O URL
```

### File Transfer (from login node)

```bash
# Secure copy
scp file.txt user@remote:/path/

# Recursive copy
scp -r directory/ user@remote:/path/

# From remote to local
scp user@remote:/path/file.txt ./

# SFTP interactive session
sftp user@remote
```

## Finding Files

### Find Command

```bash
# Find by name
find /path -name "filename.txt"

# Find by name (case-insensitive)
find /path -iname "*.txt"

# Find files modified in last 7 days
find /path -mtime -7

# Find files larger than 100MB
find /path -size +100M

# Find and execute command
find /path -name "*.tmp" -delete
find /path -name "*.txt" -exec grep "pattern" {} \;

# Find by type
find /path -type f          # Files only
find /path -type d          # Directories only
```

### Locate (Faster but uses database)

```bash
# Find files quickly
locate filename

# Update database
updatedb
```

## Environment Variables

### Common Variables

```bash
# Display variable
echo $HOME
echo $USER
echo $PATH

# Set variable
MY_VAR="value"

# Use variable
echo $MY_VAR

# Export for use in subprocesses
export MY_VAR="value"
```

### Important Environment Variables

```bash
$HOME        # Your home directory
$USER        # Your username
$PWD         # Current directory
$PATH        # Command search path
$SHELL       # Your shell
$EDITOR      # Default text editor
```

### Modify PATH

```bash
# Add to PATH (temporary)
export PATH=$PATH:/new/path

# Add to PATH (permanent, in ~/.bashrc)
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
source ~/.bashrc
```

## Shell Configuration

### Configuration Files

```bash
~/.bashrc          # Bash settings (sourced for interactive shells)
~/.bash_profile    # Login shell configuration
~/.bash_logout     # Executed on logout
```

### Customize Your Shell

**Edit ~/.bashrc**:
```bash
# Add aliases
alias ll='ls -lh'
alias la='ls -A'
alias l='ls -CF'

# Custom prompt
export PS1='\u@\h:\w\$ '

# Load modules by default
module load python/3.9
```

**Apply changes**:
```bash
source ~/.bashrc
```

## Useful Command Combinations

### System Information

```bash
# Disk space
df -h

# Memory usage
free -h

# System uptime
uptime

# Who's logged in
who
w

# Current date/time
date

# Calendar
cal
```

### Quick Data Processing

```bash
# Sort file
sort file.txt

# Sort and remove duplicates
sort file.txt | uniq

# Sort numerically
sort -n numbers.txt

# Count unique lines
sort file.txt | uniq -c

# Column processing
cut -d',' -f1,3 file.csv           # Extract columns 1 and 3
awk '{print $1, $3}' file.txt      # Print columns 1 and 3
```

### File Comparison

```bash
# Compare files
diff file1.txt file2.txt

# Side-by-side comparison
diff -y file1.txt file2.txt
```

## Tips and Tricks

### Command History

```bash
# Show command history
history

# Re-run previous command
!!

# Re-run command #123
!123

# Search history
Ctrl+R (then type to search)

# Clear history
history -c
```

### Tab Completion

- Press `Tab` to auto-complete commands and filenames
- Press `Tab` twice to see all possibilities

### Shortcuts

```bash
Ctrl+C          # Cancel current command
Ctrl+D          # Exit/logout
Ctrl+L          # Clear screen
Ctrl+A          # Move to beginning of line
Ctrl+E          # Move to end of line
Ctrl+U          # Delete to beginning of line
Ctrl+K          # Delete to end of line
Ctrl+R          # Search command history
```

### Command Chaining

```bash
# Run command2 only if command1 succeeds
command1 && command2

# Run command2 only if command1 fails
command1 || command2

# Run both regardless
command1 ; command2
```

## Job-Related Commands

### SLURM Commands (HPC Specific)

```bash
# Submit job
sbatch job.sh

# View queue
squeue -u $USER

# Cancel job
scancel JOBID

# Job details
scontrol show job JOBID

# Account information
sacct -j JOBID
```

See [SLURM Guide](../running-programs/slurm.md) for more details.

## Quick Reference Card

### Navigation
```bash
pwd                 # Print working directory
ls                  # List files
cd directory        # Change directory
```

### Files
```bash
cp source dest      # Copy
mv source dest      # Move/rename
rm file             # Delete
mkdir dir           # Create directory
```

### Viewing
```bash
cat file            # Display file
less file           # Page through file
head file           # First 10 lines
tail file           # Last 10 lines
grep pattern file   # Search in file
```

### Permissions
```bash
chmod 755 file      # Change permissions
chown user file     # Change owner
```

### Archives
```bash
tar -czf a.tar.gz dir/    # Create compressed archive
tar -xzf a.tar.gz         # Extract archive
```

### Processes
```bash
ps                  # List processes
top                 # Monitor processes
kill PID            # Kill process
```

## Practice Exercises

Try these to get comfortable:

1. **Navigate and explore**:
   ```bash
   cd ~
   pwd
   ls -la
   cd /scratch/$USER
   ```

2. **Create and manipulate files**:
   ```bash
   mkdir test
   cd test
   touch file1.txt file2.txt
   ls -l
   cp file1.txt file1_backup.txt
   mv file2.txt renamed.txt
   rm file1_backup.txt
   ```

3. **View and search**:
   ```bash
   echo "Hello World" > test.txt
   cat test.txt
   grep "Hello" test.txt
   ```

4. **Practice permissions**:
   ```bash
   echo "#!/bin/bash" > script.sh
   echo "echo 'Hello'" >> script.sh
   chmod +x script.sh
   ./script.sh
   ```

## Next Steps

- [Learn about the module system →](modules.md)
- [Start submitting jobs →](../running-programs/slurm.md)
- [Explore available software →](software.md)

## Need Help?

- **Command help**: `man command_name`
- **General Linux tutorials**: [linuxcommand.org](https://linuxcommand.org)
- **HPC support**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)