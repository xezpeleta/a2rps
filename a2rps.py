#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "matplotlib",
# ]
# ///
"""
Apache Requests Per Second (a2rps) - Analyze Apache access logs
"""

import sys
import re
import argparse
from datetime import datetime
from collections import defaultdict
import time


def parse_apache_log_line(line):
    """
    Parse a line from Apache access log.
    Common format: 127.0.0.1 - - [07/Nov/2025:22:06:24 +0000] "GET / HTTP/1.1" 200 1234
    """
    # Apache log pattern (Common Log Format and Combined Log Format)
    pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]+)" (\d+) (\S+)'
    match = re.match(pattern, line)
    
    if match:
        ip = match.group(1)
        timestamp_str = match.group(2)
        request = match.group(3)
        status = match.group(4)
        
        # Parse timestamp: 07/Nov/2025:22:06:24 +0000
        try:
            dt = datetime.strptime(timestamp_str.split()[0], '%d/%b/%Y:%H:%M:%S')
            return dt, line
        except ValueError:
            return None, line
    
    return None, line


def calculate_rps(timestamps, window_seconds=1):
    """
    Calculate requests per second from a list of timestamps.
    Groups by second and returns the count per second.
    """
    if not timestamps:
        return {}
    
    # Group by second
    counts = defaultdict(int)
    for ts in timestamps:
        # Round to the nearest second
        key = ts.replace(microsecond=0)
        counts[key] += 1
    
    return dict(sorted(counts.items()))


def filter_by_date(timestamps, fromdate=None, todate=None):
    """
    Filter timestamps by date range.
    """
    filtered = timestamps
    
    if fromdate:
        try:
            from_dt = datetime.strptime(fromdate, '%Y-%m-%d')
            filtered = [ts for ts in filtered if ts >= from_dt]
        except ValueError:
            print(f"Warning: Invalid fromdate format: {fromdate}", file=sys.stderr)
    
    if todate:
        try:
            to_dt = datetime.strptime(todate, '%Y-%m-%d')
            # Include the entire day
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            filtered = [ts for ts in filtered if ts <= to_dt]
        except ValueError:
            print(f"Warning: Invalid todate format: {todate}", file=sys.stderr)
    
    return filtered


def print_rps(rps_data):
    """
    Print RPS data to console.
    """
    if not rps_data:
        print("No data to display")
        return
    
    print("\nRequests Per Second:")
    print("-" * 50)
    for timestamp, count in rps_data.items():
        print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {count} req/s")
    
    if rps_data:
        values = list(rps_data.values())
        avg_rps = sum(values) / len(values)
        max_rps = max(values)
        min_rps = min(values)
        total_requests = sum(values)
        
        print("-" * 50)
        print(f"Total requests: {total_requests}")
        print(f"Average RPS: {avg_rps:.2f}")
        print(f"Max RPS: {max_rps}")
        print(f"Min RPS: {min_rps}")


def plot_rps(rps_data):
    """
    Create a plot of RPS data using matplotlib.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("Error: matplotlib is required for plotting. Install it with: pip install matplotlib", file=sys.stderr)
        return
    
    if not rps_data:
        print("No data to plot")
        return
    
    timestamps = list(rps_data.keys())
    values = list(rps_data.values())
    
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, marker='o', linestyle='-', linewidth=1, markersize=3)
    plt.xlabel('Time')
    plt.ylabel('Requests Per Second')
    plt.title('Apache Requests Per Second')
    plt.grid(True, alpha=0.3)
    
    # Format x-axis
    plt.gcf().autofmt_xdate()
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    
    plt.tight_layout()
    plt.show()


def follow_file(file_handle):
    """
    Generator that yields new lines from a file as they are written (like tail -f).
    """
    # Move to the end of the file
    file_handle.seek(0, 2)
    
    while True:
        line = file_handle.readline()
        if not line:
            time.sleep(0.1)  # Sleep briefly to avoid busy waiting
            continue
        yield line


def process_log_file(file_handle, follow=False, fromdate=None, todate=None, plot=False):
    """
    Process log file and calculate RPS.
    """
    timestamps = []
    
    if follow:
        print("Following log file... (Ctrl+C to stop)")
        print("-" * 50)
        
        # Process existing lines first if in follow mode
        for line in file_handle:
            dt, _ = parse_apache_log_line(line.strip())
            if dt:
                timestamps.append(dt)
        
        # Apply date filters
        if fromdate or todate:
            timestamps = filter_by_date(timestamps, fromdate, todate)
        
        # Show initial stats
        rps_data = calculate_rps(timestamps)
        if rps_data:
            values = list(rps_data.values())
            avg_rps = sum(values) / len(values) if values else 0
            print(f"Initial: {len(timestamps)} requests, Avg RPS: {avg_rps:.2f}")
            print("-" * 50)
        
        # Now follow for new lines
        try:
            for line in follow_file(file_handle):
                dt, _ = parse_apache_log_line(line.strip())
                if dt:
                    # Check date filter
                    if fromdate or todate:
                        filtered = filter_by_date([dt], fromdate, todate)
                        if not filtered:
                            continue
                    
                    timestamps.append(dt)
                    
                    # Recalculate and display current RPS
                    rps_data = calculate_rps(timestamps)
                    if rps_data:
                        latest = list(rps_data.items())[-1]
                        print(f"{latest[0].strftime('%Y-%m-%d %H:%M:%S')}: {latest[1]} req/s", end='\r')
                        sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n\nStopped following log file.")
            # Show final stats
            rps_data = calculate_rps(timestamps)
            print_rps(rps_data)
            if plot:
                plot_rps(rps_data)
    else:
        # Process all lines
        for line in file_handle:
            line = line.strip()
            if not line:
                continue
            
            dt, _ = parse_apache_log_line(line)
            if dt:
                timestamps.append(dt)
        
        # Apply date filters
        if fromdate or todate:
            timestamps = filter_by_date(timestamps, fromdate, todate)
        
        # Calculate and display RPS
        rps_data = calculate_rps(timestamps)
        
        if plot:
            plot_rps(rps_data)
        else:
            print_rps(rps_data)


def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(
        description='Apache Requests Per Second (a2rps) - Analyze Apache access logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default log file
  %(prog)s
  
  # Follow a log file in real-time
  %(prog)s -f /var/log/apache2/access.log
  
  # Generate a plot
  %(prog)s --plot /var/log/apache2/access.log
  
  # Follow and plot
  %(prog)s -f --plot /var/log/apache2/access.log
  
  # Read from stdin
  zcat /var/log/apache2/access.log.gz | %(prog)s -
  
  # Filter by date
  zcat /var/log/apache2/*access.log* | %(prog)s - --fromdate 2025-11-01
  
  # Analyze specific requests
  zcat /var/log/apache2/*access.log* | grep wp-login | %(prog)s - --fromdate 2025-11-01
        """
    )
    
    parser.add_argument(
        'logfile',
        nargs='?',
        default='/var/log/apache2/access.log',
        help='Apache log file to analyze (use - for stdin, default: /var/log/apache2/access.log)'
    )
    
    parser.add_argument(
        '-f', '--follow',
        action='store_true',
        help='Follow the log file in real-time (like tail -f)'
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate a plot instead of printing to console'
    )
    
    parser.add_argument(
        '--fromdate',
        help='Filter logs from this date (format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--todate',
        help='Filter logs to this date (format: YYYY-MM-DD)'
    )
    
    args = parser.parse_args()
    
    # Handle stdin input
    if args.logfile == '-':
        if args.follow:
            print("Error: Cannot use --follow with stdin input", file=sys.stderr)
            sys.exit(1)
        
        process_log_file(sys.stdin, follow=False, fromdate=args.fromdate, 
                        todate=args.todate, plot=args.plot)
    else:
        # Handle file input
        try:
            with open(args.logfile, 'r') as f:
                process_log_file(f, follow=args.follow, fromdate=args.fromdate,
                               todate=args.todate, plot=args.plot)
        except FileNotFoundError:
            print(f"Error: Log file not found: {args.logfile}", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied: {args.logfile}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
