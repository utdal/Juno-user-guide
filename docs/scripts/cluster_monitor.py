#!/usr/bin/env python3
"""
SLURM Cluster Node Utilization Monitor
Monitors node allocation, CPU, memory, and GPU usage across the cluster
"""

import subprocess
import re
import sys
from collections import defaultdict
import argparse
from datetime import datetime

def run_command(cmd):
    """Execute a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return None

def get_node_info():
    """Get comprehensive node information from SLURM"""
    nodes = {}

    # Get node state, CPUs, memory, and job allocation
    cmd = ['sinfo', '-N', '-h', '-o', '%N|%T|%C|%m|%G|%e|%O']
    output = run_command(cmd)

    if not output:
        return nodes

    for line in output.split('\n'):
        if not line.strip():
            continue

        parts = line.split('|')
        if len(parts) >= 6:
            node = parts[0].strip()
            state = parts[1].strip()
            cpus = parts[2].strip()  # Format: allocated/idle/other/total
            memory = parts[3].strip()  # Total memory in MB
            gres = parts[4].strip()  # GRES (GPUs)
            free_mem = parts[5].strip() if len(parts) > 5 else "0"
            cpu_load = parts[6].strip() if len(parts) > 6 else "N/A"

            # Parse CPU allocation
            cpu_parts = cpus.split('/')
            if len(cpu_parts) == 4:
                allocated_cpus = int(cpu_parts[0])
                idle_cpus = int(cpu_parts[1])
                total_cpus = int(cpu_parts[3])
            else:
                allocated_cpus = idle_cpus = total_cpus = 0

            # Parse GPU info
            gpu_count = 0
            if gres and gres != '(null)':
                gpu_match = re.search(r'gpu:(\d+)', gres)
                if gpu_match:
                    gpu_count = int(gpu_match.group(1))

            nodes[node] = {
                'state': state,
                'allocated_cpus': allocated_cpus,
                'idle_cpus': idle_cpus,
                'total_cpus': total_cpus,
                'total_memory': int(memory) if memory.isdigit() else 0,
                'free_memory': int(free_mem) if free_mem.isdigit() else 0,
                'gpu_count': gpu_count,
                'cpu_load': cpu_load
            }

    return nodes

def get_job_info():
    """Get running jobs per node"""
    node_jobs = defaultdict(list)

    cmd = ['squeue', '-h', '-o', '%N|%u|%j|%C']
    output = run_command(cmd)

    if not output:
        return node_jobs

    for line in output.split('\n'):
        if not line.strip():
            continue

        parts = line.split('|')
        if len(parts) >= 4:
            nodelist = parts[0].strip()
            user = parts[1].strip()
            jobname = parts[2].strip()
            cpus = parts[3].strip()

            # Expand node list if needed
            nodes = expand_nodelist(nodelist)
            for node in nodes:
                node_jobs[node].append({
                    'user': user,
                    'job': jobname,
                    'cpus': cpus
                })

    return node_jobs

def expand_nodelist(nodelist):
    """Expand SLURM nodelist notation (e.g., node[01-03] -> node01, node02, node03)"""
    if not nodelist or nodelist == '(null)':
        return []

    # Simple expansion for common patterns
    nodes = []
    if '[' in nodelist:
        match = re.match(r'([a-zA-Z0-9\-]+)\[([0-9,\-]+)\]', nodelist)
        if match:
            prefix = match.group(1)
            ranges = match.group(2)

            for part in ranges.split(','):
                if '-' in part:
                    start, end = part.split('-')
                    width = len(start)
                    for i in range(int(start), int(end) + 1):
                        nodes.append(f"{prefix}{str(i).zfill(width)}")
                else:
                    nodes.append(f"{prefix}{part}")
        else:
            nodes = [nodelist]
    else:
        nodes = [nodelist]

    return nodes

def create_bar(value, total, width=10):
    """Create a text-based progress bar"""
    if total == 0:
        return '[' + '░' * width + '] N/A'

    percentage = (value / total) * 100
    filled = int(width * value / total)
    bar = '█' * filled + '░' * (width - filled)
    return f'[{bar}] {percentage:4.0f}%'

def colorize_bar(bar_text, percentage):
    """Add color based on utilization percentage"""
    if percentage is None or 'N/A' in bar_text:
        return f'\033[90m{bar_text}\033[0m'  # Gray
    elif percentage < 30:
        return f'\033[92m{bar_text}\033[0m'  # Green
    elif percentage < 70:
        return f'\033[93m{bar_text}\033[0m'  # Yellow
    else:
        return f'\033[91m{bar_text}\033[0m'  # Red

def colorize_state(state):
    """Colorize node state"""
    state_colors = {
        'idle': '\033[92m',      # Green
        'allocated': '\033[93m',  # Yellow
        'mixed': '\033[96m',      # Cyan
        'down': '\033[91m',       # Red
        'drain': '\033[95m',      # Magenta
        'draining': '\033[95m',   # Magenta
    }

    color = state_colors.get(state.lower().split('+')[0], '\033[0m')
    return f'{color}{state:<12}\033[0m'

def print_summary(nodes, node_jobs):
    """Print cluster summary statistics"""
    total_nodes = len(nodes)
    idle_nodes = sum(1 for n in nodes.values() if 'idle' in n['state'].lower())
    allocated_nodes = sum(1 for n in nodes.values() if 'alloc' in n['state'].lower())
    mixed_nodes = sum(1 for n in nodes.values() if 'mix' in n['state'].lower())
    down_nodes = sum(1 for n in nodes.values() if 'down' in n['state'].lower() or 'drain' in n['state'].lower())

    total_cpus = sum(n['total_cpus'] for n in nodes.values())
    used_cpus = sum(n['allocated_cpus'] for n in nodes.values())

    total_gpus = sum(n['gpu_count'] for n in nodes.values())
    total_jobs = sum(len(jobs) for jobs in node_jobs.values())

    print(f"\n{'='*120}")
    print(f"SLURM CLUSTER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Nodes: {total_nodes} ({idle_nodes} idle, {mixed_nodes} mixed, {allocated_nodes} alloc, {down_nodes} down) | "
          f"CPUs: {used_cpus}/{total_cpus} ({100*used_cpus/total_cpus if total_cpus > 0 else 0:.0f}%) | "
          f"GPUs: {total_gpus} | Jobs: {total_jobs}")
    print(f"{'='*120}\n")

def print_node_details(nodes, node_jobs, show_idle=False, show_down=False):
    """Print detailed node information in two columns"""
    # Filter nodes based on flags
    filtered_nodes = []
    for node_name, info in sorted(nodes.items(), key=lambda x: x[0]):
        state = info['state'].lower()

        # Skip idle nodes if not requested
        if not show_idle and 'idle' in state:
            continue

        # Skip down nodes if not requested
        if not show_down and ('down' in state or 'drain' in state):
            continue

        filtered_nodes.append((node_name, info))

    if not filtered_nodes:
        print("No nodes to display with current filters.")
        return

    # Print in two columns
    mid = (len(filtered_nodes) + 1) // 2
    left_nodes = filtered_nodes[:mid]
    right_nodes = filtered_nodes[mid:]

    # Column width
    col_width = 60

    print(f"{'Node':<12} {'St':<5} {'CPU':<18} {'Mem':<18}   {'Node':<12} {'St':<5} {'CPU':<18} {'Mem':<18}")
    print(f"{'-'*12} {'-'*5} {'-'*18} {'-'*18}   {'-'*12} {'-'*5} {'-'*18} {'-'*18}")

    for i in range(len(left_nodes)):
        # Left column
        left_name, left_info = left_nodes[i]
        left_line = format_node_line(left_name, left_info, node_jobs)

        # Right column (if exists)
        if i < len(right_nodes):
            right_name, right_info = right_nodes[i]
            right_line = format_node_line(right_name, right_info, node_jobs)
            print(f"{left_line}   {right_line}")
        else:
            print(left_line)

def format_node_line(node_name, info, node_jobs):
    """Format a single node line"""
    # CPU utilization
    cpu_pct = (info['allocated_cpus'] / info['total_cpus'] * 100) if info['total_cpus'] > 0 else 0
    cpu_bar = create_bar(info['allocated_cpus'], info['total_cpus'], width=10)
    cpu_display = colorize_bar(cpu_bar, cpu_pct)

    # Memory utilization
    used_mem = info['total_memory'] - info['free_memory']
    mem_pct = (used_mem / info['total_memory'] * 100) if info['total_memory'] > 0 else 0
    mem_bar = create_bar(used_mem, info['total_memory'], width=10)
    mem_display = colorize_bar(mem_bar, mem_pct)

    # State display (shortened)
    state = info['state'][:5]
    if 'idle' in info['state'].lower():
        state_display = f'\033[92m{state:<5}\033[0m'
    elif 'alloc' in info['state'].lower():
        state_display = f'\033[93m{state:<5}\033[0m'
    elif 'mix' in info['state'].lower():
        state_display = f'\033[96m{state:<5}\033[0m'
    elif 'down' in info['state'].lower() or 'drain' in info['state'].lower():
        state_display = f'\033[91m{state:<5}\033[0m'
    else:
        state_display = f'{state:<5}'

    # Add GPU indicator
    gpu_indicator = f"[{info['gpu_count']}G]" if info['gpu_count'] > 0 else ""
    node_display = f"{node_name:<12}"
    if gpu_indicator:
        node_display = f"{node_name[:8]:<8}{gpu_indicator:<4}"

    return f"{node_display} {state_display} {cpu_display:<28} {mem_display:<28}"

def monitor_cluster(show_idle=True, show_down=False):
    """Main monitoring function"""
    nodes = get_node_info()

    if not nodes:
        print("Error: Could not retrieve node information from SLURM")
        return

    node_jobs = get_job_info()

    print_summary(nodes, node_jobs)
    print_node_details(nodes, node_jobs, show_idle, show_down)
    print(f"\n{'='*120}\n")

def main():
    parser = argparse.ArgumentParser(
        description='Monitor node utilization across SLURM cluster',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Show all nodes (default)
  %(prog)s --show-down        # Include down/drained nodes
  %(prog)s --watch            # Continuous monitoring
        """
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Show all nodes (default behavior, kept for compatibility)'
    )
    parser.add_argument(
        '--show-down',
        action='store_true',
        help='Show nodes that are down or draining'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Continuously monitor (refresh every 5 seconds)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Refresh interval in seconds for watch mode (default: 5)'
    )

    args = parser.parse_args()

    try:
        if args.watch:
            import time
            while True:
                print('\033[2J\033[H', end='')  # Clear screen
                monitor_cluster(args.all, args.show_down)
                print(f"Press Ctrl+C to stop... (refreshing every {args.interval}s)")
                time.sleep(args.interval)
        else:
            monitor_cluster(args.all, args.show_down)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()
