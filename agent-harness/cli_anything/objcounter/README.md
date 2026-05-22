# YOLO Object Counter CLI

CLI-Anything harness for **YOLO Object Counter** (目标检测计数) — an object detection and counting service using YOLOv8 ONNX models.

## Installation

```bash
cd agent-harness
pip install -e .
```

## Quick Start

```bash
# One-shot detection (no server needed)
count detect photo.jpg
count detect *.jpg --conf 0.5 -o results/

# Start the web server
count server start
count server start --port 8080 --model yolo_v8m_v11.onnx

# Check server status
count server status
count health

# Manage configuration
count config show
count config set score_threshold 0.5

# List and switch models
count model list
count model switch yolo_v8m_v11.onnx

# API key management
count key show
count key regenerate

# Detection statistics
count stats

# JSON output for scripting
count --json detect photo.jpg
```

## Commands

### `detect` — Run object detection
Direct detection using YOLOv8 ONNX — no server required. Supports batch processing.

```
count detect <images...> [--conf C] [--iou I] [--output PATH] [--model NAME]
```

### `server` — Web server management
Start/stop/restart the FastAPI web server, check status, get URLs.

```
count server start [--host H] [--port P] [--model M] [--no-auth]
count server stop
count server status
count server restart
count server url
```

### `config` — Configuration management
Read/write config.yaml settings.

```
count config show [KEY]
count config set KEY VALUE [--no-persist]
count config reset [KEY]
count config list
```

### `model` — Model management
List, inspect, switch, and warm models.

```
count model list [--server]
count model info NAME
count model switch NAME
count model warm NAME
count model warm-status
```

### `key` — API key management
Show or regenerate the server API key.

```
count key show
count key regenerate
```

### `stats` — Detection statistics
Show detection counts, averages, timing, and ScanGuard status.

```
count stats
```

### `health` — Health check
Quick server health check.

```
count health
```

## REPL Mode

Running `count` with no arguments enters interactive REPL mode:

```
count> detect photo.jpg
count> server status
count> config show score_threshold
count> json on
count> quit
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `COUNT_API_KEY` | API key for server authentication |
| `COUNT_PORT` | Server port (default: 8000) |
| `COUNT_CONFIG_PATH` | Custom config.yaml path |
