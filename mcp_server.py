"""
MCP (Model Context Protocol) Server for PMIA
WebSocket-based JSON-RPC 2.0 server for LLM agent integration

Tools exposed:
- keyboard_type
- keyboard_key
- mouse_move
- mouse_click
- jitter_on
- jitter_off
- script_run
- logs_tail
- settings_get
- settings_set
- status
"""
import json


class MCPServer:
    """
    MCP WebSocket server with JSON-RPC 2.0

    Note: This is a simplified implementation.
    Full WebSocket support requires additional libraries
    that may not be available in CircuitPython.
    """

    def __init__(self, pool, settings, usb, jitter, script_engine, logger):
        """
        Initialize MCP server

        Args:
            pool: SocketPool instance
            settings: Settings instance
            usb: USBManager instance
            jitter: JitterEngine instance
            script_engine: ScriptEngine instance
            logger: LoggingEngine instance
        """
        self.pool = pool
        self.settings = settings
        self.usb = usb
        self.jitter = jitter
        self.script_engine = script_engine
        self.logger = logger

        self.port = settings.get("mcp_port", 8080)
        self.enabled = False

        # Tool registry
        self.tools = {
            "keyboard_type": self._tool_keyboard_type,
            "keyboard_key": self._tool_keyboard_key,
            "mouse_move": self._tool_mouse_move,
            "mouse_click": self._tool_mouse_click,
            "jitter_on": self._tool_jitter_on,
            "jitter_off": self._tool_jitter_off,
            "script_run": self._tool_script_run,
            "logs_tail": self._tool_logs_tail,
            "settings_get": self._tool_settings_get,
            "settings_set": self._tool_settings_set,
            "status": self._tool_status,
        }

    def _tool_keyboard_type(self, params):
        """Tool: Type text"""
        text = params.get("text", "")
        if not text:
            return {"error": "Missing text parameter"}

        self.usb.type_text(text)
        return {"status": "ok", "length": len(text)}

    def _tool_keyboard_key(self, params):
        """Tool: Press key"""
        key = params.get("key", "")
        if not key:
            return {"error": "Missing key parameter"}

        success = self.usb.type_key(key)
        return {"status": "ok" if success else "error"}

    def _tool_mouse_move(self, params):
        """Tool: Move mouse"""
        dx = params.get("dx", 0)
        dy = params.get("dy", 0)

        success = self.usb.move_mouse(dx, dy)
        return {"status": "ok" if success else "error"}

    def _tool_mouse_click(self, params):
        """Tool: Click mouse button"""
        button = params.get("button", "left")
        count = params.get("count", 1)

        success = self.usb.click_mouse(button, count)
        return {"status": "ok" if success else "error"}

    def _tool_jitter_on(self, params):
        """Tool: Enable jitter"""
        interval = params.get("interval", None)
        if interval:
            self.jitter.set_interval(interval)

        self.jitter.enable()
        return {"status": "enabled"}

    def _tool_jitter_off(self, params):
        """Tool: Disable jitter"""
        self.jitter.disable()
        return {"status": "disabled"}

    def _tool_script_run(self, params):
        """Tool: Run script"""
        script = params.get("script", "")
        if not script:
            return {"error": "Missing script parameter"}

        success = self.script_engine.run(script)
        return {"status": "ok" if success else "error"}

    def _tool_logs_tail(self, params):
        """Tool: Get recent logs"""
        lines = params.get("lines", 50)
        logs = self.logger.tail(lines)
        return {"logs": logs}

    def _tool_settings_get(self, params):
        """Tool: Get settings"""
        # Return safe settings only
        safe_settings = {}
        for key in ["usb_mode", "jitter_interval", "log_level"]:
            safe_settings[key] = self.settings.get(key)
        return safe_settings

    def _tool_settings_set(self, params):
        """Tool: Set settings"""
        for key, value in params.items():
            if key not in ["wifi_password", "backup_password", "api_key"]:
                self.settings.set(key, value)

        self.settings.save()
        return {"status": "ok"}

    def _tool_status(self, params):
        """Tool: Get system status"""
        return {
            "usb": self.usb.stats(),
            "jitter": self.jitter.stats(),
            "script": self.script_engine.stats(),
        }

    def handle_request(self, request):
        """
        Handle JSON-RPC 2.0 request

        Args:
            request: JSON-RPC request dict

        Returns:
            JSON-RPC response dict
        """
        # Validate request
        if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
                "id": None
            }

        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        # Check if method exists
        if method not in self.tools:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": req_id
            }

        # Execute tool
        try:
            result = self.tools[method](params)

            # Check if result is an error
            if isinstance(result, dict) and "error" in result:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": result["error"]},
                    "id": req_id
                }

            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {e}"},
                "id": req_id
            }

    def get_manifest(self):
        """Get MCP tool manifest"""
        return {
            "version": "1.0",
            "tools": [
                {
                    "name": "keyboard_type",
                    "description": "Type text via USB keyboard",
                    "parameters": {"text": "string"}
                },
                {
                    "name": "keyboard_key",
                    "description": "Press a special key",
                    "parameters": {"key": "string"}
                },
                {
                    "name": "mouse_move",
                    "description": "Move mouse cursor",
                    "parameters": {"dx": "int", "dy": "int"}
                },
                {
                    "name": "mouse_click",
                    "description": "Click mouse button",
                    "parameters": {"button": "string", "count": "int"}
                },
                {
                    "name": "jitter_on",
                    "description": "Enable anti-sleep jitter",
                    "parameters": {"interval": "int (optional)"}
                },
                {
                    "name": "jitter_off",
                    "description": "Disable jitter",
                    "parameters": {}
                },
                {
                    "name": "script_run",
                    "description": "Run a macro script",
                    "parameters": {"script": "string (name or content)"}
                },
                {
                    "name": "logs_tail",
                    "description": "Get recent log entries",
                    "parameters": {"lines": "int (optional)"}
                },
                {
                    "name": "settings_get",
                    "description": "Get device settings",
                    "parameters": {}
                },
                {
                    "name": "settings_set",
                    "description": "Update device settings",
                    "parameters": {"key": "value pairs"}
                },
                {
                    "name": "status",
                    "description": "Get system status",
                    "parameters": {}
                }
            ]
        }


# Global MCP server
mcp_server = None

def init_mcp_server(pool, settings, usb, jitter, script_engine, logger):
    """Initialize global MCP server"""
    global mcp_server
    mcp_server = MCPServer(pool, settings, usb, jitter, script_engine, logger)
    return mcp_server
