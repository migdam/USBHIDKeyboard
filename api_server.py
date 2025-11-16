"""
REST API Server for PMIA
Handles HTTP requests for control and status

Endpoints:
- POST /api/type
- POST /api/key
- POST /api/mouse/move
- POST /api/mouse/click
- POST /api/mouse/scroll
- GET/POST /api/jitter/*
- GET /api/status
- GET /api/scripts/*
- POST /api/macro/run
- GET /api/logs/*
- GET /api/settings/*
- POST /api/settings/set
"""
import time
import json
import gc


class HTTPRequest:
    """Parse HTTP request"""

    def __init__(self, raw_request):
        lines = raw_request.decode('utf-8').split('\r\n')

        # Parse request line
        parts = lines[0].split(' ')
        self.method = parts[0]
        self.path = parts[1]
        self.version = parts[2] if len(parts) > 2 else 'HTTP/1.1'

        # Parse headers
        self.headers = {}
        i = 1
        while i < len(lines) and lines[i]:
            if ': ' in lines[i]:
                key, value = lines[i].split(': ', 1)
                self.headers[key.lower()] = value
            i += 1

        # Parse body
        self.body = ''
        if i + 1 < len(lines):
            self.body = '\r\n'.join(lines[i + 1:])

    def get_json(self):
        """Parse JSON body"""
        if self.body:
            try:
                return json.loads(self.body)
            except:
                return {}
        return {}


class HTTPResponse:
    """Build HTTP response"""

    def __init__(self, status=200, content_type="application/json", body=""):
        self.status = status
        self.content_type = content_type
        self.body = body

    def build(self):
        """Build response bytes"""
        status_text = {
            200: "OK",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            500: "Internal Server Error",
        }.get(self.status, "OK")

        if isinstance(self.body, dict) or isinstance(self.body, list):
            self.body = json.dumps(self.body)

        response = f"HTTP/1.1 {self.status} {status_text}\r\n"
        response += f"Content-Type: {self.content_type}\r\n"
        response += f"Content-Length: {len(self.body)}\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += self.body

        return response.encode('utf-8')


class APIServer:
    """
    HTTP REST API server
    """

    def __init__(self, pool, settings, usb, jitter, script_engine, logger, wifi_mgr):
        """
        Initialize API server

        Args:
            pool: SocketPool instance
            settings: Settings instance
            usb: USBManager instance
            jitter: JitterEngine instance
            script_engine: ScriptEngine instance
            logger: LoggingEngine instance
            wifi_mgr: WiFiManager instance
        """
        self.pool = pool
        self.settings = settings
        self.usb = usb
        self.jitter = jitter
        self.script_engine = script_engine
        self.logger = logger
        self.wifi_mgr = wifi_mgr

        self.port = settings.get("http_port", 80)
        self.api_key = settings.get("api_key", "")

        self.socket = None
        self.running = False

        # Statistics
        self.requests = 0
        self.errors = 0

    def _check_auth(self, request):
        """Check API key authentication"""
        if not self.api_key:
            return True  # No auth required

        key = request.headers.get('x-api-key', '')
        return key == self.api_key

    def _route(self, request):
        """Route request to handler"""
        path = request.path
        method = request.method

        # Authentication required for POST requests
        if method == "POST" and not self._check_auth(request):
            return HTTPResponse(401, body={"error": "Unauthorized"})

        # Keyboard endpoints
        if path == "/api/type" and method == "POST":
            return self._handle_type(request)

        elif path == "/api/key" and method == "POST":
            return self._handle_key(request)

        # Mouse endpoints
        elif path == "/api/mouse/move" and method == "POST":
            return self._handle_mouse_move(request)

        elif path == "/api/mouse/click" and method == "POST":
            return self._handle_mouse_click(request)

        elif path == "/api/mouse/scroll" and method == "POST":
            return self._handle_mouse_scroll(request)

        # Jitter endpoints
        elif path == "/api/jitter/on" and method == "POST":
            self.jitter.enable()
            return HTTPResponse(200, body={"status": "enabled"})

        elif path == "/api/jitter/off" and method == "POST":
            self.jitter.disable()
            return HTTPResponse(200, body={"status": "disabled"})

        elif path == "/api/jitter/status":
            return HTTPResponse(200, body=self.jitter.stats())

        # Status endpoint
        elif path == "/api/status":
            return self._handle_status(request)

        # Script endpoints
        elif path == "/api/scripts/list":
            scripts = self.script_engine.list_scripts()
            return HTTPResponse(200, body={"scripts": scripts})

        elif path.startswith("/api/scripts/get"):
            return self._handle_script_get(request)

        elif path == "/api/macro/run" and method == "POST":
            return self._handle_macro_run(request)

        # Log endpoints
        elif path == "/api/logs/tail":
            return self._handle_logs_tail(request)

        # Settings endpoints
        elif path == "/api/settings/get":
            return self._handle_settings_get(request)

        elif path == "/api/settings/set" and method == "POST":
            return self._handle_settings_set(request)

        # Serve Web UI
        elif path == "/" or path.startswith("/html"):
            return self._serve_static(request)

        else:
            return HTTPResponse(404, body={"error": "Not found"})

    def _handle_type(self, request):
        """Handle /api/type"""
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return HTTPResponse(400, body={"error": "Missing text"})

        self.usb.type_text(text)
        return HTTPResponse(200, body={"status": "queued", "length": len(text)})

    def _handle_key(self, request):
        """Handle /api/key"""
        data = request.get_json()
        key = data.get("key", "")

        if not key:
            return HTTPResponse(400, body={"error": "Missing key"})

        success = self.usb.type_key(key)
        return HTTPResponse(200, body={"status": "ok" if success else "error"})

    def _handle_mouse_move(self, request):
        """Handle /api/mouse/move"""
        data = request.get_json()
        dx = data.get("dx", 0)
        dy = data.get("dy", 0)

        success = self.usb.move_mouse(dx, dy)
        return HTTPResponse(200, body={"status": "ok" if success else "error"})

    def _handle_mouse_click(self, request):
        """Handle /api/mouse/click"""
        data = request.get_json()
        button = data.get("button", "left")
        count = data.get("count", 1)

        success = self.usb.click_mouse(button, count)
        return HTTPResponse(200, body={"status": "ok" if success else "error"})

    def _handle_mouse_scroll(self, request):
        """Handle /api/mouse/scroll"""
        data = request.get_json()
        amount = data.get("amount", 0)

        success = self.usb.scroll_mouse(amount)
        return HTTPResponse(200, body={"status": "ok" if success else "error"})

    def _handle_status(self, request):
        """Handle /api/status"""
        status = {
            "wifi": self.wifi_mgr.stats(),
            "usb": self.usb.stats(),
            "jitter": self.jitter.stats(),
            "script": self.script_engine.stats(),
            "uptime": time.monotonic(),
            "memory": gc.mem_free(),
            "requests": self.requests,
        }
        return HTTPResponse(200, body=status)

    def _handle_script_get(self, request):
        """Handle /api/scripts/get?name=X"""
        # Extract query parameter
        if '?' in request.path:
            query = request.path.split('?')[1]
            params = {}
            for param in query.split('&'):
                if '=' in param:
                    k, v = param.split('=', 1)
                    params[k] = v

            name = params.get('name', '')
            if name:
                script = self.script_engine.load_script(name)
                if script:
                    return HTTPResponse(200, body={"name": name, "content": script})

        return HTTPResponse(404, body={"error": "Script not found"})

    def _handle_macro_run(self, request):
        """Handle /api/macro/run"""
        data = request.get_json()
        script = data.get("script", "")

        if not script:
            return HTTPResponse(400, body={"error": "Missing script"})

        success = self.script_engine.run(script)
        return HTTPResponse(200, body={"status": "ok" if success else "error"})

    def _handle_logs_tail(self, request):
        """Handle /api/logs/tail"""
        logs = self.logger.tail(50)
        return HTTPResponse(200, body={"logs": logs})

    def _handle_settings_get(self, request):
        """Handle /api/settings/get"""
        # Return safe settings (not passwords)
        safe_settings = {}
        for key in ["usb_mode", "jitter_interval", "log_level", "mdns_hostname"]:
            safe_settings[key] = self.settings.get(key)

        return HTTPResponse(200, body=safe_settings)

    def _handle_settings_set(self, request):
        """Handle /api/settings/set"""
        data = request.get_json()

        for key, value in data.items():
            if key not in ["wifi_password", "backup_password", "ap_password"]:
                self.settings.set(key, value)

        self.settings.save()
        return HTTPResponse(200, body={"status": "ok"})

    def _serve_static(self, request):
        """Serve static Web UI files"""
        path = request.path
        if path == "/":
            path = "/html/index.html"

        # Map content types
        content_type = "text/html"
        if path.endswith(".css"):
            content_type = "text/css"
        elif path.endswith(".js"):
            content_type = "application/javascript"

        try:
            with open(path.lstrip('/'), 'r') as f:
                content = f.read()
            return HTTPResponse(200, content_type=content_type, body=content)
        except:
            return HTTPResponse(404, body="Not found")

    def start(self):
        """Start HTTP server"""
        try:
            self.socket = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_STREAM)
            self.socket.settimeout(0.1)  # Non-blocking
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(5)
            self.running = True

            print(f"API server started on port {self.port}")

        except Exception as e:
            print(f"Server start failed: {e}")
            self.running = False

    def tick(self):
        """Process incoming requests (called by scheduler)"""
        if not self.running or not self.socket:
            return

        try:
            conn, addr = self.socket.accept()
            conn.settimeout(2.0)

            # Read request
            data = b""
            while True:
                try:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                    if b"\r\n\r\n" in data:
                        break
                except:
                    break

            if data:
                self.requests += 1

                # Parse and route
                try:
                    request = HTTPRequest(data)
                    response = self._route(request)
                except Exception as e:
                    print(f"Request error: {e}")
                    response = HTTPResponse(500, body={"error": str(e)})
                    self.errors += 1

                # Send response
                conn.send(response.build())

            conn.close()

        except OSError:
            pass  # No connection available

        except Exception as e:
            print(f"Server error: {e}")
            self.errors += 1


# Global API server
api_server = None

def init_api_server(pool, settings, usb, jitter, script_engine, logger, wifi_mgr):
    """Initialize global API server"""
    global api_server
    api_server = APIServer(pool, settings, usb, jitter, script_engine, logger, wifi_mgr)
    return api_server
