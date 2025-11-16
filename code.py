"""
Pico Multi-Input Agent (PMIA)
Main entry point - orchestrates all components

Hardware: Raspberry Pi Pico 2 W
OS: CircuitPython 9.x
"""
import time
import gc
import supervisor

# Import all modules
from settings import settings
from logging_engine import logger, LogLevel
from microtasks import scheduler
from usb_manager import init_usb
from wifi_manager import init_wifi
from jitter import init_jitter
from script_engine import init_script_engine
from api_server import init_api_server
from mcp_server import init_mcp_server
from ota_updater import init_ota_updater
from button_handler import init_button_handler

# Banner
BANNER = """
╔════════════════════════════════════════╗
║   PICO MULTI-INPUT AGENT (PMIA)       ║
║   USB HID • Web UI • REST • MCP       ║
╚════════════════════════════════════════╝
"""

print(BANNER)
print("Initializing...")

# Configure logging from settings
log_level = LogLevel.from_string(settings.get("log_level", "INFO"))
logger.set_level(log_level)
logger.info("System startup")

# Display settings
print(f"USB Mode: {settings.get('usb_mode')}")
print(f"Log Level: {settings.get('log_level')}")
print(f"Jitter: {settings.get('jitter_enabled')}")

# Initialize USB HID
logger.info("Initializing USB HID")
usb_manager = init_usb(
    mode=settings.get("usb_mode", "keyboard_mouse"),
    typing_delay=settings.get("typing_delay", 10) / 1000.0
)

# Initialize WiFi
logger.info("Initializing WiFi")
wifi_mgr = init_wifi(settings)

# Connect to WiFi
logger.info("Connecting to WiFi")
if wifi_mgr.connect():
    logger.info(f"WiFi connected: {wifi_mgr.get_ip()}")
    print(f"IP Address: {wifi_mgr.get_ip()}")
    print(f"Access UI at: http://{wifi_mgr.get_ip()}")
    print(f"Or: http://{settings.get('mdns_hostname', 'pico')}.local")
else:
    logger.error("WiFi connection failed")
    print("WARNING: WiFi not connected")

# Initialize jitter engine
logger.info("Initializing jitter engine")
jitter_engine = init_jitter(
    usb_manager.mouse,
    interval=settings.get("jitter_interval", 30)
)

# Enable jitter if configured
if settings.get("jitter_enabled", False):
    jitter_engine.enable()

# Initialize script engine
logger.info("Initializing script engine")
script_eng = init_script_engine(usb_manager)

# Initialize API server
if wifi_mgr.pool:
    logger.info("Initializing API server")
    api_srv = init_api_server(
        wifi_mgr.pool,
        settings,
        usb_manager,
        jitter_engine,
        script_eng,
        logger,
        wifi_mgr
    )
    api_srv.start()

    # Initialize MCP server
    logger.info("Initializing MCP server")
    mcp_srv = init_mcp_server(
        wifi_mgr.pool,
        settings,
        usb_manager,
        jitter_engine,
        script_eng,
        logger
    )
else:
    logger.warn("No network - API server disabled")
    api_srv = None
    mcp_srv = None

# Initialize OTA updater
logger.info("Initializing OTA updater")
ota = init_ota_updater(settings)

# Initialize button handler
logger.info("Initializing button handler")
btn_handler = init_button_handler(settings, script_eng, jitter_engine)

# Setup scheduler tasks
logger.info("Setting up scheduler")

# USB keyboard queue processing (every tick)
scheduler.add_task("usb_keyboard", usb_manager.tick)

# Jitter engine (every tick, internal timing)
scheduler.add_task("jitter", jitter_engine.tick)

# Script engine (every tick, internal timing)
scheduler.add_task("script", script_eng.tick)

# WiFi monitoring (every 10s)
scheduler.add_task("wifi", wifi_mgr.tick, interval=10)

# API server (every tick for non-blocking accepts)
if api_srv:
    scheduler.add_task("api_server", api_srv.tick)

# Button handler (every 50ms for debouncing)
if btn_handler:
    scheduler.add_task("buttons", btn_handler.tick, interval=0.05)

# Logging flush (every 5s)
scheduler.add_task("log_flush", logger.tick, interval=5)

# Garbage collection (every 30s)
def gc_tick():
    gc.collect()

scheduler.add_task("gc", gc_tick, interval=30)

# Heartbeat (every 60s)
def heartbeat():
    logger.info(f"Heartbeat - Uptime: {time.monotonic():.0f}s, Memory: {gc.mem_free()} bytes")

scheduler.add_task("heartbeat", heartbeat, interval=60)

# System ready
logger.info("System ready")
print("\n" + "="*50)
print("SYSTEM READY")
print("="*50)
print(f"Uptime: {time.monotonic():.1f}s")
print(f"Free Memory: {gc.mem_free()} bytes")
print(f"Tasks: {len(scheduler.tasks)}")
print("="*50 + "\n")

# Run main loop
try:
    logger.info("Starting main loop")
    scheduler.run()

except KeyboardInterrupt:
    logger.info("Keyboard interrupt - shutting down")
    print("\nShutting down...")

except Exception as e:
    logger.error(f"Fatal error: {e}")
    print(f"\nFATAL ERROR: {e}")
    print("System halted. Please reset device.")

    # Try to log the error
    try:
        import traceback
        import sys
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stdout)
    except:
        pass

finally:
    # Cleanup
    logger.info("System shutdown")
    logger.flush()

    # Disable components
    if jitter_engine:
        jitter_engine.disable()

    if script_eng:
        script_eng.stop()

    print("Goodbye!")
