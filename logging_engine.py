"""
Logging Engine for PMIA
Provides buffered logging with rotation and SSE streaming support
"""
import time
import os
import storage

class LogLevel:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

    @staticmethod
    def from_string(s):
        return {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARN": LogLevel.WARN,
            "ERROR": LogLevel.ERROR,
        }.get(s.upper(), LogLevel.INFO)

    @staticmethod
    def to_string(level):
        return {
            LogLevel.DEBUG: "DEBUG",
            LogLevel.INFO: "INFO",
            LogLevel.WARN: "WARN",
            LogLevel.ERROR: "ERROR",
        }.get(level, "INFO")


class LoggingEngine:
    """
    Circular buffer logging with file rotation and SSE streaming
    """

    MAX_LOG_SIZE = 256 * 1024  # 256 KB
    BUFFER_SIZE = 100  # Keep last 100 log entries in memory
    FLUSH_INTERVAL = 5  # Seconds between auto-flush

    def __init__(self, log_dir="/logs", level=LogLevel.INFO):
        self.log_dir = log_dir
        self.current_file = f"{log_dir}/current.log"
        self.prev_file = f"{log_dir}/prev.log"
        self.level = level

        # In-memory circular buffer for SSE streaming
        self.buffer = []
        self.buffer_index = 0

        # SSE subscribers
        self.subscribers = []

        # Timing
        self.last_flush = time.monotonic()

        # Ensure log directory exists
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        try:
            if self.log_dir.strip("/") not in os.listdir("/"):
                os.mkdir(self.log_dir)
        except Exception as e:
            print(f"Failed to create log dir: {e}")

    def _rotate_if_needed(self):
        """Rotate logs if current.log exceeds MAX_LOG_SIZE"""
        try:
            if self.current_file.strip("/") not in os.listdir(self.log_dir):
                return

            stat = os.stat(self.current_file)
            if stat[6] >= self.MAX_LOG_SIZE:  # st_size
                # Delete old prev.log
                if self.prev_file.strip("/") in os.listdir(self.log_dir):
                    os.remove(self.prev_file)

                # Rename current to prev
                os.rename(self.current_file, self.prev_file)

                self._log_to_buffer("INFO", "Log rotated")
        except Exception as e:
            print(f"Log rotation failed: {e}")

    def _log_to_buffer(self, level_str, message):
        """Add log entry to circular buffer"""
        timestamp = time.monotonic()
        entry = {
            "time": timestamp,
            "level": level_str,
            "message": message
        }

        if len(self.buffer) < self.BUFFER_SIZE:
            self.buffer.append(entry)
        else:
            self.buffer[self.buffer_index % self.BUFFER_SIZE] = entry
            self.buffer_index += 1

        # Notify SSE subscribers
        for subscriber in self.subscribers[:]:
            try:
                subscriber(entry)
            except:
                self.subscribers.remove(subscriber)

    def _write_to_file(self, level_str, message):
        """Write log entry to file"""
        try:
            # Remount as writable
            try:
                storage.remount("/", False)
            except:
                pass

            # Rotate if needed
            self._rotate_if_needed()

            # Format log line
            timestamp = time.monotonic()
            line = f"[{timestamp:.3f}] [{level_str}] {message}\n"

            # Append to current log
            with open(self.current_file, "a") as f:
                f.write(line)

            # Remount as read-only
            try:
                storage.remount("/", True)
            except:
                pass

        except Exception as e:
            print(f"File write failed: {e}")

    def log(self, level, message):
        """Log a message"""
        if level < self.level:
            return

        level_str = LogLevel.to_string(level)

        # Add to buffer (always, for SSE)
        self._log_to_buffer(level_str, message)

        # Print to console
        print(f"[{level_str}] {message}")

    def debug(self, message):
        """Log debug message"""
        self.log(LogLevel.DEBUG, message)

    def info(self, message):
        """Log info message"""
        self.log(LogLevel.INFO, message)

    def warn(self, message):
        """Log warning message"""
        self.log(LogLevel.WARN, message)

    def error(self, message):
        """Log error message"""
        self.log(LogLevel.ERROR, message)

    def flush(self):
        """Flush buffer to file"""
        if not self.buffer:
            return

        try:
            storage.remount("/", False)
        except:
            pass

        self._rotate_if_needed()

        try:
            with open(self.current_file, "a") as f:
                for entry in self.buffer:
                    line = f"[{entry['time']:.3f}] [{entry['level']}] {entry['message']}\n"
                    f.write(line)
        except Exception as e:
            print(f"Flush failed: {e}")

        try:
            storage.remount("/", True)
        except:
            pass

        self.last_flush = time.monotonic()

    def tick(self):
        """Called by scheduler to auto-flush"""
        if time.monotonic() - self.last_flush >= self.FLUSH_INTERVAL:
            self.flush()

    def tail(self, n=50):
        """Get last N log entries from buffer"""
        if len(self.buffer) <= n:
            return self.buffer[:]

        start = self.buffer_index % self.BUFFER_SIZE
        result = []

        for i in range(n):
            idx = (start - n + i) % len(self.buffer)
            result.append(self.buffer[idx])

        return result

    def subscribe(self, callback):
        """Subscribe to SSE log stream"""
        self.subscribers.append(callback)

    def unsubscribe(self, callback):
        """Unsubscribe from SSE log stream"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def set_level(self, level):
        """Change log level"""
        if isinstance(level, str):
            self.level = LogLevel.from_string(level)
        else:
            self.level = level


# Global logger instance
logger = LoggingEngine()
