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

        # State tracking
        self.last_press_time = {}
        self.press_count = {}
        self.long_press_handled = {}

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
        """
        now = time.monotonic_ns() // 1_000_000  # Convert to ms

        for button in self.buttons:
            name = button["name"]
            pin = button["pin"]

            # Check if button is pressed (active low)
            is_pressed = not pin.value

            if is_pressed:
                # Check if this is a new press
                if name not in self.last_press_time:
                    self.last_press_time[name] = now
                    self.press_count[name] = 1
                    self.long_press_handled[name] = False

                else:
                    # Check for long press
                    press_duration = now - self.last_press_time[name]

                    if press_duration >= self.LONG_PRESS_THRESHOLD:
                        if not self.long_press_handled[name]:
                            self._handle_long_press(button)
                            self.long_press_handled[name] = True

            else:
                # Button released
                if name in self.last_press_time:
                    press_duration = now - self.last_press_time[name]

                    # Ignore if long press was handled
                    if not self.long_press_handled[name]:
                        # Check for double press
                        if name in self.press_count:
                            if self.press_count[name] == 1:
                                # Wait for potential second press
                                time.sleep(self.DOUBLE_PRESS_WINDOW / 1000.0)

                                # Check again
                                if not pin.value:
                                    # Second press detected
                                    self._handle_double_press(button)
                                    self.press_count[name] = 0
                                else:
                                    # Single press
                                    self._handle_single_press(button)

                    # Reset state
                    del self.last_press_time[name]
                    if name in self.press_count:
                        del self.press_count[name]
                    if name in self.long_press_handled:
                        del self.long_press_handled[name]


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
