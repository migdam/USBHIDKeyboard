# Quick Start Guide

Get up and running with Pico Multi-Input Agent in 5 minutes!

## What You Need

- Raspberry Pi Pico 2 W
- USB cable
- Computer to configure
- WiFi network (2.4GHz)

## Installation (5 Steps)

### 1. Flash CircuitPython

1. Download CircuitPython 9.x for Pico 2 W: https://circuitpython.org/board/raspberry_pi_pico_2_w/
2. Hold BOOTSEL button, connect Pico to computer
3. Drag `.uf2` file to RPI-RP2 drive
4. Pico reboots as CIRCUITPY

### 2. Install Libraries

1. Download library bundle: https://circuitpython.org/libraries
2. Copy `adafruit_hid/` folder to `CIRCUITPY/lib/`

### 3. Copy PMIA Files

1. Download all files from this repository
2. Copy all `.py` files to CIRCUITPY root
3. Copy `html/` and `scripts/` folders
4. Copy `settings.toml`

### 4. Configure WiFi

Edit `settings.toml`:
```toml
wifi_ssid = "YourNetwork"
wifi_password = "YourPassword"
api_key = "change-this-key"
```

### 5. Connect and Access

1. Disconnect Pico, reconnect to target computer
2. Wait 10 seconds for boot
3. Open browser to `http://pico.local`

**Done!** 🎉

## Quick Test

### Test Keyboard

1. Open Web UI
2. Go to Keyboard panel
3. Type "Hello, World!"
4. Click "Send Text"

### Test Mouse

1. Go to Mouse panel
2. Click directional arrows
3. Watch cursor move!

### Test Jitter

1. Go to Jitter panel
2. Click "Enable Jitter"
3. Watch for 1-pixel movement every 30 seconds

### Run a Macro

1. Go to Macros panel
2. Click "Refresh List"
3. Click "Preview" on "hello_world"
4. Click "Run"

## Python Control

Install client:
```bash
pip install requests
```

Use it:
```python
from pico_client import PicoClient

client = PicoClient("pico.local", api_key="your-key")
client.type_text("Automated typing!")
client.enable_jitter()
```

## Common Issues

### "Cannot find pico.local"

Try the IP address instead. Check serial console for IP:
```bash
screen /dev/ttyACM0 115200  # macOS/Linux
```

### Keyboard not typing

- Verify USB cable supports data
- Check target computer recognizes HID device
- Try different USB port

### WiFi not connecting

- Verify 2.4GHz network (not 5GHz)
- Check credentials in `settings.toml`
- Look for fallback AP: "Pico-Input-Agent"

### Web UI not loading

- Check firewall settings
- Try different browser
- Verify Pico is on same network

## Next Steps

- **Create macros:** See `MACROS.md`
- **API integration:** See `API.md`
- **Full setup:** See `SETUP.md`

## Safety Tips

- Keep API key secure
- Don't expose to internet without firewall
- Test macros before running on important systems
- Have physical access to Pico for recovery

## Getting Help

- Check documentation in this repository
- View logs in Web UI → Logs panel
- Connect serial console for debug output
- Report issues on GitHub

## Features at a Glance

✅ USB keyboard & mouse
✅ WiFi control
✅ Web UI (mobile-friendly)
✅ REST API
✅ Python client
✅ Macro scripting
✅ Anti-sleep jitter
✅ Hardware buttons
✅ MCP for LLMs
✅ OTA updates
✅ Real-time logs

Enjoy your Pico Multi-Input Agent! 🚀
