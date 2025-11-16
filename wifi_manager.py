"""
WiFi Manager for PMIA
Multi-network support with fallback AP mode
Auto-recovery and connection monitoring
"""
import time
import wifi
import socketpool

# Try to import mdns - may not be available in all CircuitPython builds
try:
    import mdns
    MDNS_AVAILABLE = True
except ImportError:
    MDNS_AVAILABLE = False
    print("WARNING: mdns module not available, mDNS will be disabled")


class WiFiManager:
    """
    Manages WiFi connectivity with multi-network support and fallback AP
    """

    # Connection states
    STATE_DISCONNECTED = 0
    STATE_CONNECTING = 1
    STATE_CONNECTED = 2
    STATE_AP_MODE = 3

    RECONNECT_INTERVAL = 30  # seconds
    MAX_RETRIES = 3

    def __init__(self, settings):
        """
        Initialize WiFi manager

        Args:
            settings: Settings instance
        """
        self.settings = settings
        self.state = self.STATE_DISCONNECTED
        self.last_attempt = 0
        self.retry_count = 0
        self.current_network = None

        # Network pool
        self.pool = None
        self.mdns_server = None

        # Statistics
        self.connect_count = 0
        self.disconnect_count = 0

    def _try_connect(self, ssid, password):
        """Attempt to connect to a network"""
        if not ssid or not password:
            return False

        try:
            print(f"Connecting to {ssid}...")
            wifi.radio.connect(ssid, password, timeout=10)

            if wifi.radio.ipv4_address:
                self.pool = socketpool.SocketPool(wifi.radio)
                self.current_network = ssid
                self.state = self.STATE_CONNECTED
                self.connect_count += 1
                self.retry_count = 0

                print(f"Connected to {ssid}")
                print(f"IP: {wifi.radio.ipv4_address}")

                # Setup mDNS
                self._setup_mdns()

                return True

        except Exception as e:
            print(f"Failed to connect to {ssid}: {e}")

        return False

    def _setup_mdns(self):
        """Setup mDNS responder"""
        if not MDNS_AVAILABLE:
            print("mDNS not available, skipping")
            return

        try:
            hostname = self.settings.get("mdns_hostname", "pico")
            self.mdns_server = mdns.Server(wifi.radio)
            self.mdns_server.hostname = hostname
            self.mdns_server.advertise_service(
                service_type="_http",
                protocol="_tcp",
                port=self.settings.get("http_port", 80)
            )
            print(f"mDNS: {hostname}.local")
        except Exception as e:
            print(f"mDNS setup failed: {e}")

    def _start_ap_mode(self):
        """Start fallback AP mode"""
        try:
            ssid = self.settings.get("ap_ssid", "Pico-Input-Agent")
            password = self.settings.get("ap_password", "PicoAgent123")

            print(f"Starting AP mode: {ssid}")

            # Check if start_ap is available
            if not hasattr(wifi.radio, 'start_ap'):
                print("AP mode not supported by this CircuitPython build")
                return False

            wifi.radio.start_ap(ssid, password)

            self.pool = socketpool.SocketPool(wifi.radio)
            self.state = self.STATE_AP_MODE
            self.current_network = ssid

            print(f"AP started: {ssid}")

            # Check if ipv4_address_ap attribute exists
            if hasattr(wifi.radio, 'ipv4_address_ap'):
                print(f"IP: {wifi.radio.ipv4_address_ap}")

            return True

        except Exception as e:
            print(f"AP mode failed: {e}")
            return False

    def connect(self):
        """
        Connect to WiFi with priority and fallback

        Priority:
        1. Primary SSID
        2. Backup SSID
        3. Fallback AP mode
        """
        # Try primary network
        if self._try_connect(
            self.settings.get("wifi_ssid"),
            self.settings.get("wifi_password")
        ):
            return True

        # Try backup network
        if self._try_connect(
            self.settings.get("backup_ssid"),
            self.settings.get("backup_password")
        ):
            return True

        # Fallback to AP mode
        print("All networks failed, starting AP mode")
        return self._start_ap_mode()

    def disconnect(self):
        """Disconnect from WiFi"""
        try:
            if self.state == self.STATE_AP_MODE:
                wifi.radio.stop_ap()
            else:
                wifi.radio.enabled = False
                wifi.radio.enabled = True

            self.state = self.STATE_DISCONNECTED
            self.disconnect_count += 1
            self.pool = None

            print("WiFi disconnected")

        except Exception as e:
            print(f"Disconnect error: {e}")

    def is_connected(self):
        """Check if connected"""
        if self.state == self.STATE_DISCONNECTED:
            return False

        # Verify connection is still active
        try:
            if self.state == self.STATE_AP_MODE:
                # Check if ap_active attribute exists
                if hasattr(wifi.radio, 'ap_active'):
                    return wifi.radio.ap_active
                else:
                    # Fallback - assume connected if in AP mode
                    return True
            else:
                return wifi.radio.ipv4_address is not None
        except:
            return False

    def get_ip(self):
        """Get current IP address"""
        try:
            if self.state == self.STATE_AP_MODE:
                return str(wifi.radio.ipv4_address_ap)
            elif self.state == self.STATE_CONNECTED:
                return str(wifi.radio.ipv4_address)
        except:
            pass
        return None

    def tick(self):
        """
        Called by scheduler to monitor connection
        Auto-reconnect if disconnected
        """
        # Check if still connected
        if self.state in (self.STATE_CONNECTED, self.STATE_AP_MODE):
            if not self.is_connected():
                print("WiFi connection lost")
                self.state = self.STATE_DISCONNECTED
                self.disconnect_count += 1

        # Try to reconnect
        if self.state == self.STATE_DISCONNECTED:
            now = time.monotonic()

            if (now - self.last_attempt) >= self.RECONNECT_INTERVAL:
                self.last_attempt = now
                self.retry_count += 1

                if self.retry_count <= self.MAX_RETRIES:
                    print(f"Reconnecting (attempt {self.retry_count})...")
                    self.connect()
                else:
                    # Too many retries, wait longer
                    if self.retry_count % 10 == 0:
                        print("Still trying to reconnect...")
                        self.connect()

    def stats(self):
        """Get WiFi statistics"""
        state_str = {
            self.STATE_DISCONNECTED: "disconnected",
            self.STATE_CONNECTING: "connecting",
            self.STATE_CONNECTED: "connected",
            self.STATE_AP_MODE: "ap_mode",
        }.get(self.state, "unknown")

        return {
            "state": state_str,
            "network": self.current_network,
            "ip": self.get_ip(),
            "connect_count": self.connect_count,
            "disconnect_count": self.disconnect_count,
            "retry_count": self.retry_count,
        }


# Global WiFi manager
wifi_manager = None

def init_wifi(settings):
    """Initialize global WiFi manager"""
    global wifi_manager
    wifi_manager = WiFiManager(settings)
    return wifi_manager
