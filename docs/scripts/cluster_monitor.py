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
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError) as e:
        # FileNotFoundError covers running this off-cluster, where scontrol/
        # squeue aren't in PATH at all - without it the caller's graceful
        # "could not retrieve node information" message is never reached.
        return None

def parse_gpu_count(gres_str):
    """
    Parse a GPU count out of a Gres/GresUsed string, e.g.:
      'gpu:a100:4(S:0-1)'                    -> 4
      'gpu:4'                                -> 4
      'gpu:nvidia_h200_nvl:2(S:3-4)'         -> 2
      'gpu:nvidia_a30_2g.12gb:4(S:4-5,10-11)' -> 4  (MIG-style type name with a period)
      '(null)' / 'N/A'                       -> 0
    Sums across multiple gpu: entries if more than one GPU type is present.
    """
    if not gres_str or gres_str in ('(null)', 'N/A', ''):
        return 0

    total = 0
    for match in re.finditer(r'gpu:(?:[\w\.\-]+:)?(\d+)', gres_str):
        total += int(match.group(1))
    return total

def parse_alloc_gpu_count(alloctres_str):
    """
    Parse the number of currently-allocated GPUs out of an AllocTRES string, e.g.:
      'cpu=48,mem=32G,gres/gpu=2,gres/gpu:nvidia_h200_nvl=2' -> 2

    Some SLURM builds don't populate GresUsed= on 'scontrol show node -o',
    so AllocTRES is the reliable source for per-node GPU allocation.

    IMPORTANT: AllocTRES lists the same allocated GPUs twice when a type is
    set - once generically ('gres/gpu=2') and once per-type
    ('gres/gpu:nvidia_h200_nvl=2'). We must prefer the generic entry and only
    fall back to summing per-type entries if the generic one is absent,
    otherwise we'd double-count.
    """
    if not alloctres_str or alloctres_str in ('(null)', 'N/A', ''):
        return 0

    generic_match = re.search(r'(?:^|,)gres/gpu=(\d+)', alloctres_str)
    if generic_match:
        return int(generic_match.group(1))

    total = 0
    for match in re.finditer(r'gres/gpu:[\w\.\-]+=(\d+)', alloctres_str):
        total += int(match.group(1))
    return total

def get_node_info():
    """Get comprehensive node information from SLURM (via scontrol, so we can
    pull both requested/allocated and idle GPU counts per node)"""
    nodes = {}

    # scontrol show node -o gives one line per node with Key=Value pairs,
    # including Gres= (total gres) and GresUsed= (currently allocated gres)
    cmd = ['scontrol', 'show', 'node', '-o']
    output = run_command(cmd)

    if not output:
        return nodes

    for line in output.split('\n'):
        if not line.strip():
            continue

        # Parse Key=Value pairs (values assumed to have no internal spaces,
        # which holds for all the fields we care about here)
        fields = dict(re.findall(r'(\S+?)=(\S*)', line))

        node_name = fields.get('NodeName')
        if not node_name:
            continue

        state = fields.get('State', 'UNKNOWN')

        cpu_alloc = int(fields.get('CPUAlloc', 0) or 0)
        cpu_tot = int(fields.get('CPUTot', 0) or 0)
        cpu_idle = max(cpu_tot - cpu_alloc, 0)

        real_memory = int(fields.get('RealMemory', 0) or 0)
        free_mem_raw = fields.get('FreeMem', '0')
        free_mem = int(free_mem_raw) if free_mem_raw.isdigit() else 0

        # AllocMem is SLURM's own bookkeeping of memory already committed to
        # jobs (in MB), as opposed to FreeMem which is OS-level "in use right
        # now". Requestable/available memory - i.e. how much a new job could
        # still ask for via --mem before SLURM would refuse/queue it - is
        # RealMemory - AllocMem, not RealMemory - FreeMem.
        alloc_mem_raw = fields.get('AllocMem', '0')
        alloc_mem = int(alloc_mem_raw) if alloc_mem_raw.isdigit() else 0
        available_requestable_mem = max(real_memory - alloc_mem, 0)

        cpu_load = fields.get('CPULoad', 'N/A')

        gres_total_str = fields.get('Gres', '')
        gres_used_str = fields.get('GresUsed', '')
        alloctres_str = fields.get('AllocTRES', '')

        gpu_total = parse_gpu_count(gres_total_str)

        # GresUsed isn't populated by every SLURM build in 'scontrol show
        # node -o' output (e.g. 24.11.5 in testing leaves it blank even for
        # nodes with active GPU jobs). AllocTRES is the reliable source, so
        # prefer it and only use GresUsed as a fallback.
        if gres_used_str and gres_used_str not in ('(null)', 'N/A'):
            gpu_allocated = parse_gpu_count(gres_used_str)
        else:
            gpu_allocated = parse_alloc_gpu_count(alloctres_str)

        gpu_idle = max(gpu_total - gpu_allocated, 0)

        nodes[node_name] = {
            'state': state,
            'allocated_cpus': cpu_alloc,
            'idle_cpus': cpu_idle,
            'total_cpus': cpu_tot,
            'total_memory': real_memory,
            'free_memory': free_mem,
            'alloc_mem': alloc_mem,
            'available_requestable_mem': available_requestable_mem,
            'gpu_count': gpu_total,
            'gpu_allocated': gpu_allocated,
            'gpu_idle': gpu_idle,
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

def format_mem_gb(mb_value):
    """Format a memory value given in MB as a GB string, e.g. 384000 -> '375G'"""
    return f"{mb_value / 1024:.0f}G"

def format_avail_mem_display(info):
    """Format the requestable/available memory column, e.g. '335G avail'"""
    avail_mb = info['available_requestable_mem']
    total_mb = info['total_memory']
    text = f"{format_mem_gb(avail_mb)} avail"

    avail_pct = (avail_mb / total_mb * 100) if total_mb > 0 else 0
    if avail_pct < 10:
        color = '\033[91m'  # Red - little room left to oversubscribe
    elif avail_pct < 30:
        color = '\033[93m'  # Yellow
    else:
        color = '\033[92m'  # Green - plenty of room

    return f'{color}{text:<14}\033[0m'

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

def classify_node_state(state):
    """
    Classify a node into exactly one bucket: 'down', 'idle', 'mixed', 'alloc',
    or 'other'. SLURM node states can be compound (e.g. 'IDLE+DRAIN',
    'MIXED+PLANNED', 'IDLE+NOT_RESPONDING'), and naively checking for
    substrings like 'idle' or 'drain' independently causes a single node to
    get counted in multiple buckets at once (an 'IDLE+DRAIN' node would match
    both an idle check and a down/drain check). That mismatch between what
    gets counted vs what gets filtered is exactly what caused idle totals in
    the summary to disagree with the number of idle rows actually shown.

    Down/drain takes priority: a node that's idle but draining can't actually
    be scheduled onto, so it's classified as 'down', not 'idle'.
    """
    s = state.lower()
    if 'down' in s or 'drain' in s or 'fail' in s or 'not_responding' in s:
        return 'down'
    elif 'idle' in s:
        return 'idle'
    elif 'mix' in s:
        return 'mixed'
    elif 'alloc' in s:
        return 'alloc'
    else:
        return 'other'

def print_summary(nodes, node_jobs):
    """Print cluster summary statistics"""
    total_nodes = len(nodes)
    idle_nodes = sum(1 for n in nodes.values() if classify_node_state(n['state']) == 'idle')
    allocated_nodes = sum(1 for n in nodes.values() if classify_node_state(n['state']) == 'alloc')
    mixed_nodes = sum(1 for n in nodes.values() if classify_node_state(n['state']) == 'mixed')
    down_nodes = sum(1 for n in nodes.values() if classify_node_state(n['state']) == 'down')

    total_cpus = sum(n['total_cpus'] for n in nodes.values())
    used_cpus = sum(n['allocated_cpus'] for n in nodes.values())

    total_mem = sum(n['total_memory'] for n in nodes.values())
    available_requestable_mem = sum(n['available_requestable_mem'] for n in nodes.values())

    total_gpus = sum(n['gpu_count'] for n in nodes.values())
    allocated_gpus = sum(n['gpu_allocated'] for n in nodes.values())
    idle_gpus = sum(n['gpu_idle'] for n in nodes.values())
    total_jobs = sum(len(jobs) for jobs in node_jobs.values())

    print(f"\n{'='*120}")
    print(f"SLURM CLUSTER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Nodes: {total_nodes} ({idle_nodes} idle, {mixed_nodes} mixed, {allocated_nodes} alloc, {down_nodes} down) | "
          f"CPUs: {used_cpus}/{total_cpus} ({100*used_cpus/total_cpus if total_cpus > 0 else 0:.0f}%) | "
          f"Mem avail to request: {format_mem_gb(available_requestable_mem)}/{format_mem_gb(total_mem)} | "
          f"GPUs: {allocated_gpus}/{total_gpus} allocated ({idle_gpus} idle) | Jobs: {total_jobs}")
    print(f"{'='*120}\n")

def print_node_details(nodes, node_jobs, show_idle=False, show_down=False):
    """Print detailed node information in two columns"""
    # Filter nodes based on flags
    filtered_nodes = []
    for node_name, info in sorted(nodes.items(), key=lambda x: x[0]):
        category = classify_node_state(info['state'])

        # Skip idle nodes if not requested
        if not show_idle and category == 'idle':
            continue

        # Skip down/drain nodes if not requested
        if not show_down and category == 'down':
            continue

        filtered_nodes.append((node_name, info))

    if not filtered_nodes:
        print("No nodes to display with current filters.")
        return

    # Print in two columns
    mid = (len(filtered_nodes) + 1) // 2
    left_nodes = filtered_nodes[:mid]
    right_nodes = filtered_nodes[mid:]

    print(f"{'Node':<12} {'St':<5} {'CPU':<18} {'Mem':<18} {'ReqAvail':<14} {'GPU':<12}   "
          f"{'Node':<12} {'St':<5} {'CPU':<18} {'Mem':<18} {'ReqAvail':<14} {'GPU':<12}")
    print(f"{'-'*12} {'-'*5} {'-'*18} {'-'*18} {'-'*14} {'-'*12}   "
          f"{'-'*12} {'-'*5} {'-'*18} {'-'*18} {'-'*14} {'-'*12}")

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

def format_gpu_display(info):
    """Format the GPU allocated/idle column, e.g. '2/4G (2 idle)'"""
    gpu_total = info['gpu_count']
    if gpu_total == 0:
        return f'\033[90m{"--":<12}\033[0m'

    gpu_alloc = info['gpu_allocated']
    gpu_idle = info['gpu_idle']
    text = f"{gpu_alloc}/{gpu_total}G ({gpu_idle} idle)"

    gpu_pct = (gpu_alloc / gpu_total * 100) if gpu_total > 0 else 0
    if gpu_pct < 30:
        color = '\033[92m'  # Green
    elif gpu_pct < 70:
        color = '\033[93m'  # Yellow
    else:
        color = '\033[91m'  # Red

    return f'{color}{text:<12}\033[0m'

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

    # GPU allocated/idle
    gpu_display = format_gpu_display(info)

    # Requestable/available memory for oversubscription planning
    avail_mem_display = format_avail_mem_display(info)

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

    node_display = f"{node_name:<12}"

    return f"{node_display} {state_display} {cpu_display:<28} {mem_display:<28} {avail_mem_display} {gpu_display}"

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
  %(prog)s                    # Show all nodes, including idle (default)
  %(prog)s --hide-idle        # Hide idle nodes
  %(prog)s --show-down        # Include down/drained nodes
  %(prog)s --watch            # Continuous monitoring
        """
    )
    parser.add_argument(
        '--hide-idle',
        action='store_true',
        help='Hide idle nodes (idle nodes are shown by default)'
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
                monitor_cluster(not args.hide_idle, args.show_down)
                print(f"Press Ctrl+C to stop... (refreshing every {args.interval}s)")
                time.sleep(args.interval)
        else:
            monitor_cluster(not args.hide_idle, args.show_down)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()
