"""
1-Pixel Jitter Engine for PMIA
Keeps computer awake with minimal cursor drift
"""
import time


class JitterEngine:
    """
    Anti-sleep jitter with symmetrical movement (no drift)

    Algorithm:
    - Move +1 px → wait → move -1 px → wait
    - Net movement: 0 (no drift)
    - Pauses during manual mouse use
    """

    MIN_INTERVAL = 20  # seconds
    MAX_INTERVAL = 120  # seconds
    DEFAULT_INTERVAL = 30

    def __init__(self, mouse_driver, interval=DEFAULT_INTERVAL):
        """
        Initialize jitter engine

        Args:
            mouse_driver: MouseDriver instance
            interval: Seconds between jitter cycles
        """
        self.mouse = mouse_driver
        self.interval = max(self.MIN_INTERVAL, min(self.MAX_INTERVAL, interval))
        self.enabled = False

        # State tracking
        self.last_jitter = 0
        self.phase = 0  # 0 = move +1, 1 = move -1
        self.jitter_count = 0
        self.paused_until = 0

    def enable(self):
        """Enable jitter"""
        self.enabled = True
        self.last_jitter = time.monotonic()
        print(f"Jitter enabled (interval: {self.interval}s)")

    def disable(self):
        """Disable jitter"""
        self.enabled = False
        print("Jitter disabled")

    def toggle(self):
        """Toggle jitter on/off"""
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def set_interval(self, interval):
        """Change jitter interval"""
        self.interval = max(self.MIN_INTERVAL, min(self.MAX_INTERVAL, interval))
        print(f"Jitter interval: {self.interval}s")

    def pause(self, duration=60):
        """
        Pause jitter (e.g., during manual mouse use)

        Args:
            duration: Pause duration in seconds
        """
        self.paused_until = time.monotonic() + duration

    def tick(self):
        """
        Called by scheduler to perform jitter
        """
        if not self.enabled:
            return

        if not self.mouse:
            return

        now = time.monotonic()

        # Check if paused
        if now < self.paused_until:
            return

        # Check if it's time to jitter
        if (now - self.last_jitter) < self.interval:
            return

        # Perform jitter movement with error handling
        try:
            if self.phase == 0:
                # Move +1 pixel right
                success = self.mouse.move(1, 0)
                if success:
                    self.phase = 1
                else:
                    # Mouse move failed, don't advance phase
                    print("Jitter: mouse move failed")
            else:
                # Move -1 pixel left (compensate)
                success = self.mouse.move(-1, 0)
                if success:
                    self.phase = 0
                    self.jitter_count += 1
                else:
                    # Mouse move failed, don't advance phase
                    print("Jitter: mouse compensation failed")

            self.last_jitter = now

        except Exception as e:
            print(f"Jitter error: {e}")
            # Don't advance phase on error to maintain symmetry

    def stats(self):
        """Get jitter statistics"""
        return {
            "enabled": self.enabled,
            "interval": self.interval,
            "jitter_count": self.jitter_count,
            "phase": self.phase,
            "paused": time.monotonic() < self.paused_until,
        }


# Global jitter instance
jitter = None

def init_jitter(mouse_driver, interval=30):
    """Initialize global jitter engine"""
    global jitter
    jitter = JitterEngine(mouse_driver, interval)
    return jitter
