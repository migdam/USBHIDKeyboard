"""
USB Manager for PMIA
Coordinates keyboard and mouse operations
"""
from keyboard import init_keyboard
from mouse import init_mouse


class USBManager:
    """
    Manages USB HID devices (keyboard and mouse)
    """

    def __init__(self, mode="keyboard_mouse", typing_delay=0.01):
        """
        Initialize USB manager

        Args:
            mode: "keyboard", "mouse", or "keyboard_mouse"
            typing_delay: Delay between keystrokes
        """
        self.mode = mode
        self.keyboard = None
        self.mouse = None

        # Initialize devices based on mode
        if mode in ("keyboard", "keyboard_mouse"):
            self.keyboard = init_keyboard(typing_delay=typing_delay)

        if mode in ("mouse", "keyboard_mouse"):
            self.mouse = init_mouse()

    def tick(self):
        """Process USB operations (called by scheduler)"""
        if self.keyboard:
            self.keyboard.tick()

    def type_text(self, text):
        """Type text via keyboard"""
        if not self.keyboard:
            return False
        self.keyboard.type_text(text)
        return True

    def type_key(self, key):
        """Press special key"""
        if not self.keyboard:
            return False
        return self.keyboard.type_key(key)

    def type_combo(self, *keys):
        """Press key combination"""
        if not self.keyboard:
            return False
        return self.keyboard.type_combo(*keys)

    def move_mouse(self, dx, dy):
        """Move mouse cursor"""
        if not self.mouse:
            return False
        return self.mouse.move(dx, dy)

    def click_mouse(self, button="left", count=1):
        """Click mouse button"""
        if not self.mouse:
            return False

        button_map = {
            "left": self.mouse.LEFT_BUTTON,
            "right": self.mouse.RIGHT_BUTTON,
            "middle": self.mouse.MIDDLE_BUTTON,
        }

        btn = button_map.get(button.lower(), self.mouse.LEFT_BUTTON)
        return self.mouse.click(btn, count)

    def scroll_mouse(self, amount):
        """Scroll mouse wheel"""
        if not self.mouse:
            return False
        return self.mouse.scroll(amount)

    def is_busy(self):
        """Check if USB operations are in progress"""
        if self.keyboard:
            return self.keyboard.is_busy()
        return False

    def stats(self):
        """Get USB statistics"""
        stats = {"mode": self.mode}

        if self.keyboard:
            stats["keyboard"] = self.keyboard.stats()

        if self.mouse:
            stats["mouse"] = self.mouse.stats()

        return stats


# Global USB manager
usb_manager = None

def init_usb(mode="keyboard_mouse", typing_delay=0.01):
    """Initialize global USB manager"""
    global usb_manager
    usb_manager = USBManager(mode=mode, typing_delay=typing_delay)
    return usb_manager
