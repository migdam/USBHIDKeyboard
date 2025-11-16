# Changelog

All notable changes to Pico Multi-Input Agent will be documented in this file.

## [1.0.0] - 2025-11-16

### Initial Release

#### Core Features
- USB HID keyboard support with adaptive chunking
- USB HID mouse support (move, click, scroll)
- 1-pixel anti-sleep jitter engine (no drift)
- WiFi manager with multi-network support and fallback AP
- Microtask scheduler for cooperative multitasking
- Comprehensive logging with rotation and buffering
- Settings management via TOML

#### Automation
- Script/macro engine with custom DSL
- Support for text typing, key presses, mouse control
- Hardware button triggers for macros
- Repeat loops and timing control

#### Network Control
- REST API server with full endpoint suite
- Modern mobile-friendly Web UI
- Real-time status monitoring
- Log streaming

#### Integration
- MCP (Model Context Protocol) server for LLM agents
- Python client library for easy integration
- JSON-RPC 2.0 interface

#### Management
- OTA firmware update framework
- Web-based configuration
- Safe mode for recovery
- mDNS support (pico.local)

#### Documentation
- Comprehensive setup guide
- API documentation
- Macro scripting guide
- Example scripts included

### Components

#### Firmware Modules
- `code.py` - Main entry point
- `settings.py` - Settings manager
- `logging_engine.py` - Logging system
- `microtasks.py` - Cooperative scheduler
- `keyboard.py` - HID keyboard driver
- `mouse.py` - HID mouse driver
- `usb_manager.py` - USB coordination
- `wifi_manager.py` - Network management
- `jitter.py` - Anti-sleep jitter
- `script_engine.py` - Macro DSL interpreter
- `api_server.py` - REST API server
- `mcp_server.py` - MCP server
- `ota_updater.py` - Firmware updates
- `button_handler.py` - GPIO button handling

#### Web UI
- `html/index.html` - Main UI
- `html/style.css` - Light theme
- `html/dark.css` - Dark theme
- `html/app.js` - UI logic

#### Tools
- `pico_client.py` - Python API client
- Example macros in `/scripts/`

#### Documentation
- `README.md` - Project overview
- `SETUP.md` - Installation guide
- `API.md` - API reference
- `MACROS.md` - Scripting guide
- `LICENSE` - MIT license

### Technical Specifications

- **Platform:** Raspberry Pi Pico 2 W
- **OS:** CircuitPython 9.x
- **Language:** Python 3
- **Protocol:** USB HID 1.1
- **Network:** WiFi 2.4GHz, HTTP, WebSocket
- **Memory:** Optimized for <200KB RAM usage
- **Performance:** <20ms typing latency, <5ms scheduler tick

### Known Limitations

- No BLE HID support
- WiFi 5GHz not supported (hardware limitation)
- Limited to 2MB firmware size
- No cloud integration
- Simplified WebSocket implementation (no full SSL/TLS)

### Future Roadmap

- Enhanced repeat block support (multi-line)
- Variable support in macro DSL
- Conditional execution
- File upload via Web UI
- Real-time log streaming via SSE
- Advanced error recovery
- Performance profiling tools
- Custom keyboard layouts

## Development

- **Repository:** https://github.com/migdam/USBHIDKeyboard
- **Issues:** Report bugs via GitHub Issues
- **Contributions:** Pull requests welcome

## License

MIT License - See LICENSE file for details
