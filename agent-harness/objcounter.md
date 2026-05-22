# YOLO Object Counter — count

## Target software

**YOLO Object Counter (目标检测计数)** — a FastAPI web service for object detection and counting using YOLOv8 ONNX models.

Source path: `<project_root>/`

## Mode: One-shot detection + server management

The harness operates in two modes:
1. **Direct detection**: Uses `ObjectDetector` directly (imports the project package) — no server required
2. **Server API**: Communicates with a running FastAPI server via HTTP for model switching, stats, key management, etc.

## Command architecture

```
count
├── detect <images...>      # One-shot: run YOLO inference directly
├── server                  # Server lifecycle (subprocess management)
│   ├── start
│   ├── stop
│   ├── status
│   ├── restart
│   └── url
├── config                  # YAML config read/write
│   ├── show [key]
│   ├── set <key> <value>
│   ├── reset [key]
│   └── list
├── model                   # Model listing/switching/warming
│   ├── list
│   ├── info <name>
│   ├── switch <name>
│   ├── warm <name>
│   └── warm-status
├── key                     # API key operations
│   ├── show
│   └── regenerate
├── stats                   # Detection statistics
├── health                  # Health check
└── (default)               # REPL interactive mode
```

## State model

- **REPL session state**: JSON output toggle (`json on/off`), API key, port
- **No undo/redo** — the target software has no native undo support

## Backend mapping

| CLI command | Backend | Notes |
|-------------|---------|-------|
| `detect` | `DetectorBackend` (direct import) | No server needed |
| `detect --server` | `CountAPIClient.detect()` | Via HTTP |
| `server *` | `ServerBackend` (subprocess) | PID file tracking |
| `config *` | `ConfigBackend` (YAML read/write) | Direct file I/O |
| `model list` | `DetectorBackend.list_models()` | Direct filesystem |
| `model switch/warm` | `CountAPIClient` | Requires running server |
| `key *` | `CountAPIClient` | Requires running server |
| `stats` | `CountAPIClient` | Requires running server |
| `health` | `CountAPIClient` | Requires running server |

## JSON output

All commands support `--json` flag (or `json on` in REPL) for machine-readable JSON output.

## Limitations

- `model switch/warm`, `key`, `stats`, `health` require a running server
- Server subprocess management uses PID files — stale state possible after crashes
- No streaming support for detection results
- Direct detection does not use the ValuablePhotoSaver (no auto-save of low-confidence images)
