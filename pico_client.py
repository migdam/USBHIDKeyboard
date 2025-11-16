"""
Python API Client for Pico Multi-Input Agent
Easy-to-use library for controlling PMIA from Python scripts
"""
import requests
from typing import Optional, Dict, Any, List


class PicoClient:
    """
    Python client for Pico Multi-Input Agent REST API

    Usage:
        client = PicoClient("192.168.1.100", api_key="your-key")
        client.type_text("Hello, World!")
        client.enable_jitter(interval=30)
        client.run_macro("hello_world")
    """

    def __init__(self, host: str, port: int = 80, api_key: Optional[str] = None):
        """
        Initialize client

        Args:
            host: IP address or hostname of Pico device
            port: HTTP port (default 80)
            api_key: API key for authentication
        """
        self.base_url = f"http://{host}:{port}"
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({"X-API-Key": api_key})

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    # Keyboard Methods

    def type_text(self, text: str) -> Dict[str, Any]:
        """
        Type text via USB keyboard

        Args:
            text: Text to type

        Returns:
            Response dict with status
        """
        return self._post("/api/type", {"text": text})

    def press_key(self, key: str) -> Dict[str, Any]:
        """
        Press a special key

        Args:
            key: Key name (e.g., "ENTER", "TAB", "ESC")

        Returns:
            Response dict with status
        """
        return self._post("/api/key", {"key": key})

    # Mouse Methods

    def move_mouse(self, dx: int, dy: int) -> Dict[str, Any]:
        """
        Move mouse cursor (relative)

        Args:
            dx: Horizontal movement (pixels)
            dy: Vertical movement (pixels)

        Returns:
            Response dict with status
        """
        return self._post("/api/mouse/move", {"dx": dx, "dy": dy})

    def click_mouse(self, button: str = "left", count: int = 1) -> Dict[str, Any]:
        """
        Click mouse button

        Args:
            button: Button to click ("left", "right", "middle")
            count: Number of clicks

        Returns:
            Response dict with status
        """
        return self._post("/api/mouse/click", {"button": button, "count": count})

    def scroll_mouse(self, amount: int) -> Dict[str, Any]:
        """
        Scroll mouse wheel

        Args:
            amount: Scroll amount (positive = up, negative = down)

        Returns:
            Response dict with status
        """
        return self._post("/api/mouse/scroll", {"amount": amount})

    # Jitter Methods

    def enable_jitter(self, interval: Optional[int] = None) -> Dict[str, Any]:
        """
        Enable anti-sleep jitter

        Args:
            interval: Optional jitter interval in seconds

        Returns:
            Response dict with status
        """
        return self._post("/api/jitter/on", {})

    def disable_jitter(self) -> Dict[str, Any]:
        """
        Disable jitter

        Returns:
            Response dict with status
        """
        return self._post("/api/jitter/off", {})

    def get_jitter_status(self) -> Dict[str, Any]:
        """
        Get jitter status

        Returns:
            Status dict with enabled, interval, count
        """
        return self._get("/api/jitter/status")

    # Script/Macro Methods

    def list_scripts(self) -> List[str]:
        """
        List available scripts

        Returns:
            List of script names
        """
        response = self._get("/api/scripts/list")
        return response.get("scripts", [])

    def get_script(self, name: str) -> str:
        """
        Get script content

        Args:
            name: Script name

        Returns:
            Script content as string
        """
        response = self._get("/api/scripts/get", {"name": name})
        return response.get("content", "")

    def run_macro(self, script: str) -> Dict[str, Any]:
        """
        Run a macro script

        Args:
            script: Script name or raw script content

        Returns:
            Response dict with status
        """
        return self._post("/api/macro/run", {"script": script})

    # Status & Logs

    def get_status(self) -> Dict[str, Any]:
        """
        Get system status

        Returns:
            Status dict with wifi, usb, jitter, uptime, memory
        """
        return self._get("/api/status")

    def get_logs(self, lines: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent log entries

        Args:
            lines: Number of log lines to retrieve

        Returns:
            List of log entry dicts
        """
        response = self._get("/api/logs/tail")
        return response.get("logs", [])

    # Settings

    def get_settings(self) -> Dict[str, Any]:
        """
        Get device settings

        Returns:
            Settings dict
        """
        return self._get("/api/settings/get")

    def set_settings(self, **kwargs) -> Dict[str, Any]:
        """
        Update device settings

        Args:
            **kwargs: Settings key-value pairs

        Returns:
            Response dict with status
        """
        return self._post("/api/settings/set", kwargs)

    # Convenience Methods

    def type_and_enter(self, text: str):
        """Type text and press ENTER"""
        self.type_text(text)
        self.press_key("ENTER")

    def draw_square(self, size: int = 100, delay: float = 0.5):
        """Draw a square with the mouse"""
        import time
        self.move_mouse(size, 0)
        time.sleep(delay)
        self.move_mouse(0, size)
        time.sleep(delay)
        self.move_mouse(-size, 0)
        time.sleep(delay)
        self.move_mouse(0, -size)

    def keep_alive(self, duration: int = 3600):
        """
        Keep computer awake for specified duration

        Args:
            duration: Duration in seconds (default 1 hour)
        """
        self.enable_jitter()
        import time
        time.sleep(duration)
        self.disable_jitter()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = PicoClient("pico.local", api_key="your-api-key")

    # Type some text
    print("Typing text...")
    client.type_text("Hello from Python!")
    client.press_key("ENTER")

    # Check status
    print("\nSystem status:")
    status = client.get_status()
    print(f"WiFi: {status['wifi']['state']}")
    print(f"Uptime: {status['uptime']:.0f}s")
    print(f"Memory: {status['memory']} bytes")

    # Enable jitter
    print("\nEnabling jitter...")
    client.enable_jitter()

    # List available scripts
    print("\nAvailable scripts:")
    scripts = client.list_scripts()
    for script in scripts:
        print(f"  - {script}")

    # Run a script
    if scripts:
        print(f"\nRunning script: {scripts[0]}")
        client.run_macro(scripts[0])

    print("\nDone!")
