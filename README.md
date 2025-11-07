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

```bash
uv pip install git+https://github.com/xezpeleta/a2rps.git --system
```

Using `uv` you can also run it directly without installation:

```bash
uv run --with=matplotlib https://xezpeleta.github.io/a2rps/a2rps.py
```

### Using pip

```bash
pip install git+https://github.com/xezpeleta/a2rps.git --system
```

## Usage

### Basic usage

By default, reads `/var/log/apache2/access.log`:

```bash
$ uv run a2rps
...
2025-11-08 00:13:23: 1 req/s
2025-11-08 00:14:05: 1 req/s
2025-11-08 00:14:30: 1 req/s
2025-11-08 00:15:02: 1 req/s
--------------------------------------------------
Total requests: 53
Average RPS: 1.00
Max RPS: 1
Min RPS: 1
```

### Specify a log file

```bash
uv run a2rps /var/log/apache2/myvhost_access.log
```

### Follow a log file in real-time

![Example plot generated with a2rps](assets/a2rps.png "Example plot image generated with a2rps")

```bash
uv run a2rps -f /var/log/apache2/access.log
```

### Generate a plot

Save plot to default location (a2rps.png):

```bash
uv run a2rps /var/log/apache2/access.log --plot
```

Save plot to custom location:

```bash
uv run a2rps /var/log/apache2/access.log --plot ~/my_plot.png
```

Note: When using `--plot`, the `-f` (follow) flag is ignored.

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

## Examples

### Analyze an incident

Analyze wp-login and xmlrpc requests:

```bash
zcat -f /var/log/apache2/*access.log* | grep -i -e wp-login -e xmlrpc | uv run a2rps - --fromdate 2025-11-01
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
  --plot [PATH]        Save plot to file (default: a2rps.png if no path specified)
  --fromdate FROMDATE  Filter logs from this date (format: YYYY-MM-DD)
  --todate TODATE      Filter logs to this date (format: YYYY-MM-DD)
```

## License

See LICENSE file for details.
