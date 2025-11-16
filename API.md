# API Documentation - Pico Multi-Input Agent

## REST API Endpoints

All POST endpoints require authentication via `X-API-Key` header.

Base URL: `http://pico.local` or `http://<ip-address>`

### Keyboard Endpoints

#### POST /api/type
Type text via USB keyboard

**Request:**
```json
{
  "text": "Hello, World!"
}
```

**Response:**
```json
{
  "status": "queued",
  "length": 13
}
```

#### POST /api/key
Press a special key

**Request:**
```json
{
  "key": "ENTER"
}
```

**Supported keys:** ENTER, TAB, ESC, BACKSPACE, DELETE, UP, DOWN, LEFT, RIGHT, HOME, END, PAGE_UP, PAGE_DOWN, F1-F12, CTRL, ALT, SHIFT, GUI

**Response:**
```json
{
  "status": "ok"
}
```

### Mouse Endpoints

#### POST /api/mouse/move
Move mouse cursor (relative movement)

**Request:**
```json
{
  "dx": 100,
  "dy": 50
}
```

**Response:**
```json
{
  "status": "ok"
}
```

#### POST /api/mouse/click
Click mouse button

**Request:**
```json
{
  "button": "left",
  "count": 1
}
```

**Buttons:** left, right, middle

**Response:**
```json
{
  "status": "ok"
}
```

#### POST /api/mouse/scroll
Scroll mouse wheel

**Request:**
```json
{
  "amount": 5
}
```

Positive = scroll up, Negative = scroll down

**Response:**
```json
{
  "status": "ok"
}
```

### Jitter Endpoints

#### POST /api/jitter/on
Enable anti-sleep jitter

**Response:**
```json
{
  "status": "enabled"
}
```

#### POST /api/jitter/off
Disable jitter

**Response:**
```json
{
  "status": "disabled"
}
```

#### GET /api/jitter/status
Get jitter status

**Response:**
```json
{
  "enabled": true,
  "interval": 30,
  "jitter_count": 42,
  "phase": 0,
  "paused": false
}
```

### Script Endpoints

#### GET /api/scripts/list
List available scripts

**Response:**
```json
{
  "scripts": ["hello_world.txt", "example_loop.txt"]
}
```

#### GET /api/scripts/get?name=hello_world
Get script content

**Response:**
```json
{
  "name": "hello_world.txt",
  "content": "type \"Hello, World!\"\npress ENTER"
}
```

#### POST /api/macro/run
Run a script

**Request:**
```json
{
  "script": "hello_world"
}
```

Or provide raw script:
```json
{
  "script": "type \"Direct script\"\npress ENTER"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### Status & Logs

#### GET /api/status
Get system status

**Response:**
```json
{
  "wifi": {
    "state": "connected",
    "network": "MyNetwork",
    "ip": "192.168.1.100"
  },
  "usb": {
    "mode": "keyboard_mouse",
    "keyboard": {
      "chars_sent": 1234,
      "errors": 0,
      "is_busy": false
    },
    "mouse": {
      "moves": 56,
      "clicks": 12
    }
  },
  "jitter": {
    "enabled": true,
    "jitter_count": 42
  },
  "uptime": 3600,
  "memory": 102400,
  "requests": 123
}
```

#### GET /api/logs/tail
Get recent log entries

**Response:**
```json
{
  "logs": [
    {
      "time": 1234.567,
      "level": "INFO",
      "message": "System ready"
    }
  ]
}
```

### Settings Endpoints

#### GET /api/settings/get
Get device settings (safe settings only)

**Response:**
```json
{
  "usb_mode": "keyboard_mouse",
  "jitter_interval": 30,
  "log_level": "INFO",
  "mdns_hostname": "pico"
}
```

#### POST /api/settings/set
Update settings

**Request:**
```json
{
  "usb_mode": "keyboard",
  "log_level": "DEBUG",
  "jitter_interval": 60
}
```

**Response:**
```json
{
  "status": "ok"
}
```

## Python Client Library

### Installation

```bash
pip install requests
```

### Usage

```python
from pico_client import PicoClient

# Initialize client
client = PicoClient("pico.local", api_key="your-key")

# Type text
client.type_text("Hello, World!")

# Press keys
client.press_key("ENTER")

# Move mouse
client.move_mouse(100, 50)

# Click
client.click_mouse("left")

# Enable jitter
client.enable_jitter()

# Run macro
client.run_macro("hello_world")

# Get status
status = client.get_status()
print(f"Uptime: {status['uptime']}s")
```

## MCP Server

The MCP server provides JSON-RPC 2.0 interface for LLM agents.

**Endpoint:** `ws://pico.local/mcp` (WebSocket)

**Manifest:** `http://pico.local/mcp/manifest.json`

### Available Tools

- `keyboard_type(text)` - Type text
- `keyboard_key(key)` - Press key
- `mouse_move(dx, dy)` - Move mouse
- `mouse_click(button)` - Click button
- `jitter_on(interval)` - Enable jitter
- `jitter_off()` - Disable jitter
- `script_run(script)` - Run script
- `logs_tail(lines)` - Get logs
- `settings_get()` - Get settings
- `settings_set(**kwargs)` - Set settings
- `status()` - Get status

### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "keyboard_type",
  "params": {
    "text": "Hello from MCP"
  },
  "id": 1
}
```

### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "length": 14
  },
  "id": 1
}
```

## Authentication

POST endpoints require API key authentication:

```
X-API-Key: your-api-key
```

Set your API key in `settings.toml`:

```toml
api_key = "your-secure-key"
```

## Rate Limiting

Currently no rate limiting is implemented. Use responsibly.

## Error Responses

Errors return standard HTTP status codes:

- `400` - Bad Request (missing parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `500` - Internal Server Error

**Example error:**
```json
{
  "error": "Missing text parameter"
}
```
