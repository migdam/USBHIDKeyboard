"""
Settings Manager for PMIA
Handles reading/writing settings.toml with type validation
"""
import os
import storage

class Settings:
    """Manages device settings with defaults and validation"""

    DEFAULTS = {
        "wifi_ssid": "",
        "wifi_password": "",
        "backup_ssid": "",
        "backup_password": "",
        "ap_ssid": "Pico-Input-Agent",
        "ap_password": "PicoAgent123",
        "api_key": "change-this-secure-key",
        "usb_mode": "keyboard_mouse",
        "jitter_interval": 30,
        "jitter_enabled": False,
        "log_level": "INFO",
        "adaptive_chunking": True,
        "chunk_size": 256,
        "button1_pin": 15,
        "button1_script": "macro1",
        "button2_pin": 14,
        "button2_action": "toggle_jitter",
        "enable_ota": True,
        "mdns_hostname": "pico",
        "http_port": 80,
        "mcp_port": 8080,
        "typing_delay": 10,
    }

    def __init__(self, config_file="settings.toml"):
        self.config_file = config_file
        self._settings = {}
        self.load()

    def load(self):
        """Load settings from TOML file"""
        self._settings = self.DEFAULTS.copy()

        if self.config_file not in os.listdir("/"):
            return  # Use defaults

        try:
            with open(self.config_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        elif value.isdigit():
                            value = int(value)

                        if key in self._settings:
                            self._settings[key] = value
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save(self):
        """Save settings to TOML file"""
        try:
            # Remount filesystem as writable
            try:
                storage.remount("/", False)
            except:
                pass  # Already writable

            with open(self.config_file, "w") as f:
                f.write("# Pico Multi-Input Agent Configuration\n")
                f.write("# Auto-generated - Edit with caution\n\n")

                sections = {
                    "WiFi Settings": ["wifi_ssid", "wifi_password", "backup_ssid",
                                     "backup_password", "ap_ssid", "ap_password"],
                    "Security": ["api_key"],
                    "USB Configuration": ["usb_mode"],
                    "Jitter Settings": ["jitter_interval", "jitter_enabled"],
                    "Logging": ["log_level"],
                    "Performance": ["adaptive_chunking", "chunk_size"],
                    "Hardware Buttons": ["button1_pin", "button1_script",
                                         "button2_pin", "button2_action"],
                    "OTA Updates": ["enable_ota"],
                    "Network": ["mdns_hostname", "http_port", "mcp_port"],
                    "Typing Speed": ["typing_delay"],
                }

                for section, keys in sections.items():
                    f.write(f"# {section}\n")
                    for key in keys:
                        if key in self._settings:
                            value = self._settings[key]
                            if isinstance(value, bool):
                                value = str(value).lower()
                            elif isinstance(value, str):
                                value = f'"{value}"'
                            f.write(f"{key} = {value}\n")
                    f.write("\n")

            # Remount as read-only
            try:
                storage.remount("/", True)
            except:
                pass

        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        if key in self.DEFAULTS:
            self._settings[key] = value
            return True
        return False

    def __getitem__(self, key):
        """Allow dict-like access"""
        return self._settings[key]

    def __setitem__(self, key, value):
        """Allow dict-like setting"""
        self.set(key, value)

# Global settings instance
settings = Settings()
