# Pico Multi-Input Agent (PMIA)

**Robust USB HID Keyboard & Mouse • Web UI • REST API • MCP Server • Scripts • Macros • Logging • Jitter Engine • OTA • Modern UI**

## Overview

The Pico Multi-Input Agent transforms the Raspberry Pi Pico 2 W into a fully autonomous multi-interface automation device capable of:

- Acting as a USB HID **keyboard** and **mouse**
- Receiving commands via a **modern Web UI**, **REST API**, or **Model Context Protocol (MCP) Server**
- Executing **local scripts/macros** stored on the device
- Providing **mouse jitter** to keep the target computer awake
- Hosting a Web UI locally (mobile-friendly, offline)
- Delivering **real-time logs** via SSE
- Managing settings and firmware updates (OTA)

## Hardware Requirements

- Raspberry Pi Pico 2 W
- USB cable for connection to target computer
- Optional: GPIO button for hardware triggers

## Features

### USB HID
- Full keyboard support (US layout, ASCII + special characters)
- Mouse control (move, click, scroll)
- Adaptive chunking for long text (up to 100KB+)
- Non-blocking queue-based operation

### Automation
- Script/macro engine with custom DSL
- Hardware button triggers
- 1-pixel anti-sleep jitter (no drift)
- Scheduled task execution

### Network Control
- REST API with authentication
- MCP WebSocket server for LLM agents
- Modern web UI (mobile-friendly)
- Real-time log streaming via SSE

### Management
- WiFi manager (multi-network, fallback AP mode)
- Settings via settings.toml
- OTA firmware updates
- Comprehensive logging with rotation

## Quick Start

1. Flash CircuitPython 9.x to your Pico 2 W
2. Copy all files to CIRCUITPY drive
3. Edit `settings.toml` with your WiFi credentials
4. Reboot the device
5. Access web UI at `http://pico.local` or the displayed IP address

## API Access

```python
import requests

# Configure API key
headers = {"X-API-Key": "your-api-key"}

# Type text
requests.post("http://pico.local/api/type",
              json={"text": "Hello World"},
              headers=headers)

# Enable jitter
requests.post("http://pico.local/api/jitter/on", headers=headers)
```

## MCP Integration

Connect LLM agents (Claude Desktop, ChatGPT) via WebSocket at `ws://pico.local/mcp`

## File Structure

```
/
├── code.py                 # Main entry point
├── settings.toml           # Configuration
├── microtasks.py          # Cooperative scheduler
├── wifi_manager.py        # Network management
├── usb_manager.py         # USB coordination
├── keyboard.py            # HID keyboard driver
├── mouse.py               # HID mouse driver
├── jitter.py              # Anti-sleep jitter engine
├── script_engine.py       # Macro DSL interpreter
├── logging_engine.py      # Logging with rotation
├── ota_updater.py         # Firmware updates
├── mcp_server.py          # MCP WebSocket server
├── api_server.py          # REST API server
├── settings.py            # Settings manager
├── /html/                 # Web UI files
│   ├── index.html
│   ├── style.css
│   ├── dark.css
│   └── app.js
├── /scripts/              # User macros
│   └── example.txt
└── /logs/                 # Log files
    ├── current.log
    └── prev.log
```

## License

MIT License

## Author

Built for autonomous USB HID automation on Raspberry Pi Pico 2 W
