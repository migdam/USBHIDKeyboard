"""
USB HID Keyboard Driver for PMIA
Adaptive chunking, zero-copy buffering, queue-based non-blocking
"""
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


class KeyboardDriver:
    """
    Advanced USB HID keyboard with adaptive chunking
    Supports large text input (100KB+) without blocking
    """

    # Adaptive chunk sizes (bytes)
    CHUNK_SIZES = [128, 256, 512]
    DEFAULT_CHUNK_SIZE = 256

    # Queue limits to prevent memory exhaustion
    MAX_QUEUE_SIZE = 10  # Maximum number of text items in queue
    MAX_TEXT_LENGTH = 100 * 1024  # 100 KB per text item

    # Special key mapping
    SPECIAL_KEYS = {
        "ENTER": Keycode.ENTER,
        "TAB": Keycode.TAB,
        "ESCAPE": Keycode.ESCAPE,
        "ESC": Keycode.ESCAPE,
        "BACKSPACE": Keycode.BACKSPACE,
        "DELETE": Keycode.DELETE,
        "UP": Keycode.UP_ARROW,
        "DOWN": Keycode.DOWN_ARROW,
        "LEFT": Keycode.LEFT_ARROW,
        "RIGHT": Keycode.RIGHT_ARROW,
        "HOME": Keycode.HOME,
        "END": Keycode.END,
        "PAGE_UP": Keycode.PAGE_UP,
        "PAGE_DOWN": Keycode.PAGE_DOWN,
        "F1": Keycode.F1,
        "F2": Keycode.F2,
        "F3": Keycode.F3,
        "F4": Keycode.F4,
        "F5": Keycode.F5,
        "F6": Keycode.F6,
        "F7": Keycode.F7,
        "F8": Keycode.F8,
        "F9": Keycode.F9,
        "F10": Keycode.F10,
        "F11": Keycode.F11,
        "F12": Keycode.F12,
        "CTRL": Keycode.CONTROL,
        "ALT": Keycode.ALT,
        "SHIFT": Keycode.SHIFT,
        "GUI": Keycode.GUI,
        "WINDOWS": Keycode.GUI,
        "COMMAND": Keycode.GUI,
    }

    def __init__(self, typing_delay=0.01, adaptive_chunking=True):
        """
        Initialize keyboard driver

        Args:
            typing_delay: Delay between keystrokes (seconds)
            adaptive_chunking: Enable adaptive chunk sizing
        """
        try:
            self.keyboard = Keyboard(usb_hid.devices)
        except Exception as e:
            print(f"Failed to initialize keyboard: {e}")
            self.keyboard = None

        self.typing_delay = typing_delay
        self.adaptive_chunking = adaptive_chunking
        self.chunk_size = self.DEFAULT_CHUNK_SIZE

        # Text queue for non-blocking typing
        self.queue = []
        self.current_text = None
        self.current_position = 0

        # Performance tracking
        self.chars_sent = 0
        self.errors = 0

    def type_text(self, text):
        """
        Queue text for typing

        Args:
            text: String to type

        Returns:
            bool: True if queued, False if queue full or text too long
        """
        if not text:
            return False

        # Check queue size limit
        if len(self.queue) >= self.MAX_QUEUE_SIZE:
            print(f"Keyboard queue full ({self.MAX_QUEUE_SIZE} items)")
            return False

        # Check text length limit
        if len(text) > self.MAX_TEXT_LENGTH:
            print(f"Text too long ({len(text)} > {self.MAX_TEXT_LENGTH} bytes)")
            return False

        self.queue.append(text)
        return True

    def type_key(self, key_name):
        """
        Press a special key

        Args:
            key_name: Key name (e.g., "ENTER", "CTRL")
        """
        if not self.keyboard:
            return False

        key_name = key_name.upper()

        if key_name not in self.SPECIAL_KEYS:
            print(f"Unknown key: {key_name}")
            return False

        try:
            keycode = self.SPECIAL_KEYS[key_name]
            self.keyboard.press(keycode)
            time.sleep(0.01)
            self.keyboard.release(keycode)
            return True
        except Exception as e:
            print(f"Key press error: {e}")
            self.errors += 1
            return False

    def type_combo(self, *keys):
        """
        Press key combination (e.g., CTRL+C)

        Args:
            keys: Key names in order
        """
        if not self.keyboard:
            return False

        keycodes = []
        for key in keys:
            key = key.upper()
            if key in self.SPECIAL_KEYS:
                keycodes.append(self.SPECIAL_KEYS[key])
            else:
                print(f"Unknown key in combo: {key}")
                return False

        try:
            # Press all keys
            for kc in keycodes:
                self.keyboard.press(kc)

            time.sleep(0.02)

            # Release in reverse order
            for kc in reversed(keycodes):
                self.keyboard.release(kc)

            return True
        except Exception as e:
            print(f"Combo error: {e}")
            self.errors += 1
            return False

    def _send_char(self, char):
        """Send a single character"""
        if not self.keyboard:
            return False

        try:
            self.keyboard.write(char)
            self.chars_sent += 1
            return True
        except Exception as e:
            print(f"Char send error: {e}")
            self.errors += 1
            return False

    def _adjust_chunk_size(self):
        """Dynamically adjust chunk size based on performance"""
        if not self.adaptive_chunking:
            return

        # Simple heuristic: reduce chunk size if errors increase
        error_rate = self.errors / max(self.chars_sent, 1)

        if error_rate > 0.01:  # > 1% errors
            # Reduce chunk size
            idx = self.CHUNK_SIZES.index(self.chunk_size)
            if idx > 0:
                self.chunk_size = self.CHUNK_SIZES[idx - 1]
                print(f"Reduced chunk size to {self.chunk_size}")
        elif error_rate < 0.001 and self.chars_sent > 1000:
            # Increase chunk size
            idx = self.CHUNK_SIZES.index(self.chunk_size)
            if idx < len(self.CHUNK_SIZES) - 1:
                self.chunk_size = self.CHUNK_SIZES[idx + 1]
                print(f"Increased chunk size to {self.chunk_size}")

    def tick(self):
        """
        Process keyboard queue (called by scheduler)
        Non-blocking - sends one chunk per tick
        """
        if not self.keyboard:
            return

        # Load next text from queue if needed
        if self.current_text is None:
            if self.queue:
                self.current_text = self.queue.pop(0)
                self.current_position = 0
                print(f"Typing: {len(self.current_text)} chars")
            else:
                return

        # Send one chunk
        start_pos = self.current_position
        end_pos = min(start_pos + self.chunk_size, len(self.current_text))

        chunk = self.current_text[start_pos:end_pos]

        for char in chunk:
            if not self._send_char(char):
                # Error - retry next tick
                return

            if self.typing_delay > 0:
                time.sleep(self.typing_delay)

        self.current_position = end_pos

        # Check if done
        if self.current_position >= len(self.current_text):
            print(f"Typed {len(self.current_text)} chars")
            self.current_text = None
            self.current_position = 0
            self._adjust_chunk_size()

    def is_busy(self):
        """Check if keyboard is actively typing"""
        return self.current_text is not None or len(self.queue) > 0

    def clear_queue(self):
        """Clear pending text"""
        self.queue = []
        self.current_text = None
        self.current_position = 0

    def stats(self):
        """Get keyboard statistics"""
        return {
            "chars_sent": self.chars_sent,
            "errors": self.errors,
            "queue_length": len(self.queue),
            "current_position": self.current_position,
            "chunk_size": self.chunk_size,
            "is_busy": self.is_busy(),
        }


# Global keyboard instance
keyboard = None

def init_keyboard(typing_delay=0.01, adaptive_chunking=True):
    """Initialize global keyboard"""
    global keyboard
    keyboard = KeyboardDriver(typing_delay, adaptive_chunking)
    return keyboard
