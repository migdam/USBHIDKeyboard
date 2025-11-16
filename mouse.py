"""
USB HID Mouse Driver for PMIA
Relative movement, clicks, scroll wheel
"""
import time
import usb_hid
from adafruit_hid.mouse import Mouse


class MouseDriver:
    """
    USB HID mouse control
    """

    # Mouse buttons
    LEFT_BUTTON = Mouse.LEFT_BUTTON
    RIGHT_BUTTON = Mouse.RIGHT_BUTTON
    MIDDLE_BUTTON = Mouse.MIDDLE_BUTTON

    def __init__(self, movement_multiplier=1.0):
        """
        Initialize mouse driver

        Args:
            movement_multiplier: Scale movement distances
        """
        try:
            self.mouse = Mouse(usb_hid.devices)
        except Exception as e:
            print(f"Failed to initialize mouse: {e}")
            self.mouse = None

        self.movement_multiplier = movement_multiplier

        # Statistics
        self.moves = 0
        self.clicks = 0
        self.scrolls = 0
        self.errors = 0

    def move(self, dx, dy):
        """
        Move mouse cursor (relative)

        Args:
            dx: Horizontal movement (pixels, -127 to 127)
            dy: Vertical movement (pixels, -127 to 127)
        """
        if not self.mouse:
            return False

        try:
            # Apply multiplier
            dx = int(dx * self.movement_multiplier)
            dy = int(dy * self.movement_multiplier)

            # Clamp to valid range
            dx = max(-127, min(127, dx))
            dy = max(-127, min(127, dy))

            self.mouse.move(x=dx, y=dy)
            self.moves += 1
            return True

        except Exception as e:
            print(f"Mouse move error: {e}")
            self.errors += 1
            return False

    def click(self, button=LEFT_BUTTON, count=1):
        """
        Click mouse button

        Args:
            button: Button to click (LEFT_BUTTON, RIGHT_BUTTON, MIDDLE_BUTTON)
            count: Number of clicks
        """
        if not self.mouse:
            return False

        try:
            for _ in range(count):
                self.mouse.click(button)
                time.sleep(0.05)  # Debounce
                self.clicks += 1

            return True

        except Exception as e:
            print(f"Mouse click error: {e}")
            self.errors += 1
            return False

    def press(self, button=LEFT_BUTTON):
        """Press and hold mouse button"""
        if not self.mouse:
            return False

        try:
            self.mouse.press(button)
            return True
        except Exception as e:
            print(f"Mouse press error: {e}")
            self.errors += 1
            return False

    def release(self, button=LEFT_BUTTON):
        """Release mouse button"""
        if not self.mouse:
            return False

        try:
            self.mouse.release(button)
            return True
        except Exception as e:
            print(f"Mouse release error: {e}")
            self.errors += 1
            return False

    def scroll(self, amount):
        """
        Scroll wheel

        Args:
            amount: Scroll amount (positive = up, negative = down)
        """
        if not self.mouse:
            return False

        try:
            # Clamp to valid range
            amount = max(-127, min(127, amount))

            self.mouse.move(wheel=amount)
            self.scrolls += 1
            return True

        except Exception as e:
            print(f"Mouse scroll error: {e}")
            self.errors += 1
            return False

    def stats(self):
        """Get mouse statistics"""
        return {
            "moves": self.moves,
            "clicks": self.clicks,
            "scrolls": self.scrolls,
            "errors": self.errors,
        }


# Global mouse instance
mouse = None

def init_mouse(movement_multiplier=1.0):
    """Initialize global mouse"""
    global mouse
    mouse = MouseDriver(movement_multiplier)
    return mouse
