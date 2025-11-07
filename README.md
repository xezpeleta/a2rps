# a2rps
Apache Requests Per Second

Analyze Apache access logs and calculate requests per second (RPS) metrics.

## Features

- Calculate and display requests per second from Apache access logs
- Real-time log following (like `tail -f`)
- Generate plots with matplotlib
- Filter logs by date range
- Support for piped input (stdin)
- Compatible with Astral's `uv` tool

## Installation

### Using uv (recommended)

Run directly without installation:

```bash
uv run --with=matplotlib https://xezpeleta.github.io/a2rps/a2rps.py
```

Or install it:

```bash
uv pip install git+https://github.com/xezpeleta/a2rps.git
```

### Using pip

```bash
pip install git+https://github.com/xezpeleta/a2rps.git --system
```

## Usage

### Basic usage

By default, reads `/var/log/apache2/access.log`:

```bash
uv run a2rps
```

### Specify a log file

```bash
uv run a2rps /var/log/apache2/myvhost_access.log
```

### Follow a log file in real-time

```bash
uv run a2rps -f /var/log/apache2/access.log
```

### Generate a plot

```bash
uv run a2rps --plot /var/log/apache2/access.log
```

### Combine follow and plot

```bash
uv run a2rps -f --plot /var/log/apache2/access.log
```

### Read from stdin (pipe logs)

```bash
zcat -f /var/log/apache2/*access.log* | uv run a2rps -
```

### Filter by date

```bash
zcat -f /var/log/apache2/*access.log* | uv run a2rps - --fromdate 2025-11-01
```

```bash
zcat -f /var/log/apache2/*access.log* | uv run a2rps - --fromdate 2025-11-01 --todate 2025-11-07
```

### Analyze specific requests

Analyze wp-login and xmlrpc attacks:

```bash
zcat -f /var/log/apache2/*access.log* | grep -i -e wp-login -e xmlrpc | uv run --with=matplotlib a2rps.py - --fromdate 2025-11-01
```

## Examples

### Analyze an incident

```bash
zcat -f /var/log/apache2/*access.log* | grep -i -e wp-login -e xmlrpc | uv run --with=matplotlib a2rps.py - --fromdate 2025-11-01
```

### Monitor real-time traffic

```bash
uv run a2rps -f /var/log/apache2/access.log
```

### Generate historical report

```bash
uv run a2rps --plot /var/log/apache2/access.log
```

## Command-line Options

```
positional arguments:
  logfile              Apache log file to analyze (use - for stdin, 
                       default: /var/log/apache2/access.log)

optional arguments:
  -h, --help           show this help message and exit
  -f, --follow         Follow the log file in real-time (like tail -f)
  --plot               Generate a plot instead of printing to console
  --fromdate FROMDATE  Filter logs from this date (format: YYYY-MM-DD)
  --todate TODATE      Filter logs to this date (format: YYYY-MM-DD)
```

## License

See LICENSE file for details.
