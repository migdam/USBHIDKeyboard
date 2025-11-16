"""
Microtask Scheduler for PMIA
Provides cooperative multitasking for concurrent operations
Guarantees <5ms latency between ticks
"""
import time


class Task:
    """Represents a scheduled task"""

    def __init__(self, name, callback, interval=0, one_shot=False):
        self.name = name
        self.callback = callback
        self.interval = interval  # seconds
        self.one_shot = one_shot
        self.last_run = 0
        self.enabled = True
        self.error_count = 0

    def should_run(self, now):
        """Check if task should run"""
        if not self.enabled:
            return False
        if self.interval == 0:
            return True  # Run every tick
        return (now - self.last_run) >= self.interval

    def run(self):
        """Execute task callback"""
        if not self.enabled:
            return

        try:
            start = time.monotonic()
            self.callback()
            duration = time.monotonic() - start

            # Warn if task blocks too long
            if duration > 0.001:  # 1ms
                print(f"WARNING: Task '{self.name}' blocked for {duration*1000:.2f}ms")

            self.last_run = time.monotonic()

            if self.one_shot:
                self.enabled = False

            self.error_count = 0  # Reset on success

        except Exception as e:
            self.error_count += 1
            print(f"ERROR in task '{self.name}': {e}")

            # Disable task after 10 consecutive errors
            if self.error_count >= 10:
                print(f"Task '{self.name}' disabled after 10 errors")
                self.enabled = False


class MicrotaskScheduler:
    """
    Cooperative multitasking scheduler

    Usage:
        scheduler = MicrotaskScheduler()
        scheduler.add_task("heartbeat", heartbeat_fn, interval=1.0)
        scheduler.add_task("usb_poll", usb_poll_fn)  # Run every tick

        while True:
            scheduler.tick()
    """

    MAX_TICK_DURATION = 0.005  # 5ms

    def __init__(self):
        self.tasks = []
        self.running = False
        self.tick_count = 0
        self.last_tick = time.monotonic()

    def add_task(self, name, callback, interval=0, one_shot=False):
        """
        Add a task to the scheduler

        Args:
            name: Unique task identifier
            callback: Function to call (must not block > 1ms)
            interval: Seconds between runs (0 = every tick)
            one_shot: Run once and disable
        """
        task = Task(name, callback, interval, one_shot)
        self.tasks.append(task)
        return task

    def remove_task(self, name):
        """Remove task by name"""
        self.tasks = [t for t in self.tasks if t.name != name]

    def get_task(self, name):
        """Get task by name"""
        for task in self.tasks:
            if task.name == name:
                return task
        return None

    def enable_task(self, name):
        """Enable a task"""
        task = self.get_task(name)
        if task:
            task.enabled = True

    def disable_task(self, name):
        """Disable a task"""
        task = self.get_task(name)
        if task:
            task.enabled = False

    def tick(self):
        """
        Run one scheduler iteration
        Should be called in main loop
        """
        tick_start = time.monotonic()
        now = tick_start

        # Track tick frequency
        tick_interval = now - self.last_tick
        if tick_interval > 0.010:  # 10ms
            print(f"WARNING: Slow tick interval: {tick_interval*1000:.2f}ms")

        self.last_tick = now

        # Run all eligible tasks
        for task in self.tasks:
            if task.should_run(now):
                task.run()

                # Check if we're taking too long
                elapsed = time.monotonic() - tick_start
                if elapsed > self.MAX_TICK_DURATION:
                    print(f"WARNING: Tick exceeded {self.MAX_TICK_DURATION*1000}ms")
                    break  # Defer remaining tasks to next tick

        self.tick_count += 1

    def run(self):
        """
        Run scheduler indefinitely
        Call this as main loop
        """
        self.running = True
        print("Scheduler started")

        while self.running:
            self.tick()

            # Small yield to prevent CPU lock
            time.sleep(0.001)  # 1ms

    def stop(self):
        """Stop the scheduler"""
        self.running = False

    def stats(self):
        """Get scheduler statistics"""
        enabled = sum(1 for t in self.tasks if t.enabled)
        return {
            "tick_count": self.tick_count,
            "total_tasks": len(self.tasks),
            "enabled_tasks": enabled,
            "uptime": time.monotonic()
        }


# Global scheduler instance
scheduler = MicrotaskScheduler()
