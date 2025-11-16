# Setup Guide - Pico Multi-Input Agent

## Hardware Requirements

- Raspberry Pi Pico 2 W
- USB cable (for connecting to target computer)
- Optional: GPIO buttons for hardware triggers

## Software Requirements

- CircuitPython 9.x for Raspberry Pi Pico 2 W
- Required CircuitPython libraries:
  - `adafruit_hid` (for USB keyboard/mouse)

## Installation Steps

### 1. Flash CircuitPython

1. Download CircuitPython 9.x for Raspberry Pi Pico 2 W from:
   https://circuitpython.org/board/raspberry_pi_pico_2_w/

2. Hold the BOOTSEL button on your Pico 2 W while connecting it to your computer via USB

3. The Pico will appear as a USB drive named "RPI-RP2"

4. Copy the downloaded `.uf2` file to the drive

5. The Pico will reboot and appear as "CIRCUITPY"

### 2. Install Required Libraries

1. Download the CircuitPython library bundle from:
   https://circuitpython.org/libraries

2. Extract the bundle and copy these libraries to `CIRCUITPY/lib/`:
   - `adafruit_hid/` (entire folder)

### 3. Copy PMIA Files

1. Copy all Python files to the root of CIRCUITPY:
   - `code.py`
   - `settings.py`
   - `logging_engine.py`
   - `microtasks.py`
   - `keyboard.py`
   - `mouse.py`
   - `jitter.py`
   - `script_engine.py`
   - `wifi_manager.py`
   - `usb_manager.py`
   - `api_server.py`
   - `mcp_server.py`
   - `ota_updater.py`
   - `button_handler.py`

2. Copy the `html/` folder to CIRCUITPY

3. Copy the `scripts/` folder to CIRCUITPY

4. Copy `settings.toml` to CIRCUITPY

### 4. Configure WiFi

1. Edit `settings.toml` on the CIRCUITPY drive

2. Update these settings:
   ```toml
   wifi_ssid = "YourNetworkName"
   wifi_password = "YourPassword"
   api_key = "your-secure-api-key"
   ```

3. Save the file

### 5. Connect Hardware

1. Disconnect the Pico from your computer

2. Connect the Pico to your target computer via USB

3. The Pico will:
   - Boot and initialize all systems
   - Connect to WiFi
   - Start the Web UI and API server
   - Become available as a USB HID device

### 6. Find Your Pico

The Pico will be accessible at:
- `http://pico.local` (if mDNS is supported)
- IP address displayed on USB serial console
- Fallback AP: `Pico-Input-Agent` (if WiFi fails)

## Accessing the Serial Console

To view boot messages and debug output:

1. Connect to the Pico's serial console using:
   - **Windows**: PuTTY, TeraTerm
   - **macOS/Linux**: `screen /dev/ttyACM0 115200`

2. Press Ctrl+D to reload the code

## Troubleshooting

### Pico not appearing as USB HID device

- Check USB cable (must support data, not just power)
- Verify CircuitPython is properly installed
- Check USB mode in `settings.toml`

### Cannot connect to WiFi

- Verify WiFi credentials in `settings.toml`
- Check WiFi network is 2.4GHz (Pico W doesn't support 5GHz)
- Look for fallback AP: `Pico-Input-Agent`

### Web UI not loading

- Check IP address in serial console
- Verify firewall settings on your computer
- Try accessing via IP instead of `pico.local`

### Keyboard/Mouse not working

- Ensure target computer recognizes USB HID device
- Check `usb_mode` setting in `settings.toml`
- Try different USB port

## Next Steps

Once installed, you can:

1. Access the Web UI to control the device
2. Use the Python client library (`pico_client.py`)
3. Create custom macros in `/scripts/`
4. Integrate with LLM agents via MCP

See `API.md` for API documentation and `MACROS.md` for macro scripting guide.
