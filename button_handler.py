"""
Hardware Button Handler for PMIA
Manages GPIO button inputs for macro triggers and jitter control
"""
import time
import board
import digitalio


class ButtonHandler:
    """
    Handles hardware button inputs with debouncing

    Features:
    - Single press: Run assigned macro
    - Double press: Toggle jitter
    - Long press: Enter safe mode
    """

    DEBOUNCE_MS = 50
    DOUBLE_PRESS_WINDOW = 500  # ms
    LONG_PRESS_THRESHOLD = 2000  # ms

    def __init__(self, settings, script_engine, jitter_engine):
        """
        Initialize button handler

        Args:
            settings: Settings instance
            script_engine: ScriptEngine instance
            jitter_engine: JitterEngine instance
        """
        self.settings = settings
        self.script_engine = script_engine
        self.jitter_engine = jitter_engine

        # Button configuration
        self.buttons = []
        self._setup_buttons()

        # State tracking (per button)
        self.button_state = {}  # Consolidated state per button

        # States: 'idle', 'pressed', 'released_waiting', 'long_press_triggered'
        for btn in self.buttons:
            self.button_state[btn["name"]] = {
                "state": "idle",
                "press_start": 0,
                "release_time": 0,
                "long_press_handled": False
            }

    def _setup_buttons(self):
        """Setup GPIO buttons from settings"""
        # Button 1
        try:
            pin1 = self.settings.get("button1_pin", 15)
            btn1 = digitalio.DigitalInOut(getattr(board, f"GP{pin1}"))
            btn1.direction = digitalio.Direction.INPUT
            btn1.pull = digitalio.Pull.UP  # Active low

            self.buttons.append({
                "pin": btn1,
                "name": "button1",
                "action": self.settings.get("button1_script", "macro1")
            })
        except Exception as e:
            print(f"Button 1 setup failed: {e}")

        # Button 2
        try:
            pin2 = self.settings.get("button2_pin", 14)
            btn2 = digitalio.DigitalInOut(getattr(board, f"GP{pin2}"))
            btn2.direction = digitalio.Direction.INPUT
            btn2.pull = digitalio.Pull.UP  # Active low

            self.buttons.append({
                "pin": btn2,
                "name": "button2",
                "action": self.settings.get("button2_action", "toggle_jitter")
            })
        except Exception as e:
            print(f"Button 2 setup failed: {e}")

    def _handle_single_press(self, button):
        """Handle single button press"""
        action = button["action"]

        if action == "toggle_jitter":
            self.jitter_engine.toggle()
        else:
            # Assume it's a script name
            print(f"Running macro: {action}")
            self.script_engine.run(action)

    def _handle_double_press(self, button):
        """Handle double button press"""
        print(f"Double press: {button['name']}")
        self.jitter_engine.toggle()

    def _handle_long_press(self, button):
        """Handle long button press"""
        print(f"Long press: {button['name']} - Entering safe mode")
        # Safe mode: disable all automation
        self.jitter_engine.disable()
        self.script_engine.stop()
        print("Safe mode activated")

    def tick(self):
        """
        Poll buttons (called by scheduler)
        Non-blocking state machine implementation
        """
        try:
            now = time.monotonic() * 1000  # Convert to ms
        except AttributeError:
            # Fallback for older CircuitPython
            now = time.monotonic() * 1000

        for button in self.buttons:
            name = button["name"]
            pin = button["pin"]
            state = self.button_state[name]

            # Check if button is pressed (active low)
            is_pressed = not pin.value

            # State machine
            if state["state"] == "idle":
                if is_pressed:
                    # Button pressed - transition to pressed state
                    state["state"] = "pressed"
                    state["press_start"] = now
                    state["long_press_handled"] = False

            elif state["state"] == "pressed":
                if is_pressed:
                    # Still pressed - check for long press
                    press_duration = now - state["press_start"]
                    if press_duration >= self.LONG_PRESS_THRESHOLD:
                        if not state["long_press_handled"]:
                            self._handle_long_press(button)
                            state["long_press_handled"] = True
                            state["state"] = "long_press_triggered"
                else:
                    # Button released
                    if not state["long_press_handled"]:
                        # Start waiting for potential double press
                        state["state"] = "released_waiting"
                        state["release_time"] = now
                    else:
                        # Long press was handled, return to idle
                        state["state"] = "idle"

            elif state["state"] == "released_waiting":
                if is_pressed:
                    # Second press detected - double press!
                    self._handle_double_press(button)
                    state["state"] = "idle"
                else:
                    # Check if double-press window expired
                    wait_duration = now - state["release_time"]
                    if wait_duration >= self.DOUBLE_PRESS_WINDOW:
                        # Single press confirmed
                        self._handle_single_press(button)
                        state["state"] = "idle"

            elif state["state"] == "long_press_triggered":
                if not is_pressed:
                    # Long press released, return to idle
                    state["state"] = "idle"


# Global button handler
button_handler = None

def init_button_handler(settings, script_engine, jitter_engine):
    """Initialize global button handler"""
    global button_handler
    try:
        button_handler = ButtonHandler(settings, script_engine, jitter_engine)
        return button_handler
    except Exception as e:
        print(f"Button handler init failed: {e}")
        return None
