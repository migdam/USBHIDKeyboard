"""
Script/Macro Engine for PMIA
DSL parser and interpreter for automation scripts

Supported commands:
- type "text"
- press KEY
- wait 100
- repeat N { ... }
- click left/right/middle
- move dx dy
"""
import time
import os


class ScriptParser:
    """Parses macro DSL"""

    @staticmethod
    def parse(script_text):
        """
        Parse script into command list

        Returns: List of (command, args) tuples
        """
        commands = []
        lines = script_text.strip().split('\n')

        for line_no, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            try:
                cmd = ScriptParser._parse_line(line)
                if cmd:
                    commands.append(cmd)
            except Exception as e:
                raise SyntaxError(f"Line {line_no}: {e}")

        return commands

    @staticmethod
    def _parse_line(line):
        """Parse a single command line"""
        # type "text"
        if line.startswith('type '):
            text = line[5:].strip()
            if text.startswith('"') and text.endswith('"'):
                return ('type', text[1:-1])
            else:
                raise SyntaxError("type requires quoted string")

        # press KEY
        elif line.startswith('press '):
            key = line[6:].strip()
            return ('press', key)

        # wait milliseconds
        elif line.startswith('wait '):
            ms = int(line[5:].strip())
            return ('wait', ms / 1000.0)  # Convert to seconds

        # repeat N { ... }
        elif line.startswith('repeat '):
            parts = line[7:].split('{')
            count = int(parts[0].strip())
            # Note: This is simplified - full implementation would need
            # multi-line block parsing
            return ('repeat', count)

        # click button
        elif line.startswith('click '):
            button = line[6:].strip()
            return ('click', button)

        # move dx dy
        elif line.startswith('move '):
            parts = line[5:].strip().split()
            dx = int(parts[0])
            dy = int(parts[1])
            return ('move', (dx, dy))

        # scroll amount
        elif line.startswith('scroll '):
            amount = int(line[7:].strip())
            return ('scroll', amount)

        else:
            raise SyntaxError(f"Unknown command: {line}")


class ScriptEngine:
    """
    Executes macro scripts line-by-line (non-blocking)
    """

    def __init__(self, usb_manager, script_dir="/scripts"):
        """
        Initialize script engine

        Args:
            usb_manager: USBManager instance
            script_dir: Directory containing scripts
        """
        self.usb = usb_manager
        self.script_dir = script_dir

        # Execution state
        self.running = False
        self.commands = []
        self.pc = 0  # Program counter
        self.wait_until = 0
        self.repeat_stack = []  # (start_pc, remaining_count)

        # Statistics
        self.scripts_run = 0
        self.errors = 0

        # Ensure script directory exists
        self._ensure_script_dir()

    def _ensure_script_dir(self):
        """Create script directory if needed"""
        try:
            if self.script_dir.strip("/") not in os.listdir("/"):
                os.mkdir(self.script_dir)
        except Exception as e:
            print(f"Script dir creation failed: {e}")

    def list_scripts(self):
        """List available scripts"""
        try:
            files = os.listdir(self.script_dir)
            return [f for f in files if f.endswith('.txt')]
        except:
            return []

    def load_script(self, name):
        """Load script from file"""
        if not name.endswith('.txt'):
            name += '.txt'

        path = f"{self.script_dir}/{name}"

        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Script load error: {e}")
            return None

    def run(self, script_name_or_text):
        """
        Start running a script

        Args:
            script_name_or_text: Script filename or raw script text
        """
        if self.running:
            print("Script already running")
            return False

        # Check if it's a filename
        if '\n' not in script_name_or_text and len(script_name_or_text) < 50:
            script_text = self.load_script(script_name_or_text)
            if not script_text:
                return False
        else:
            script_text = script_name_or_text

        # Parse script
        try:
            self.commands = ScriptParser.parse(script_text)
        except SyntaxError as e:
            print(f"Script syntax error: {e}")
            self.errors += 1
            return False

        # Start execution
        self.running = True
        self.pc = 0
        self.wait_until = 0
        self.repeat_stack = []
        self.scripts_run += 1

        print(f"Script started ({len(self.commands)} commands)")
        return True

    def stop(self):
        """Stop running script"""
        self.running = False
        self.pc = 0
        print("Script stopped")

    def tick(self):
        """
        Execute one script instruction (called by scheduler)
        """
        if not self.running:
            return

        # Check if waiting
        if time.monotonic() < self.wait_until:
            return

        # Check if done
        if self.pc >= len(self.commands):
            # Check repeat stack
            if self.repeat_stack:
                start_pc, remaining = self.repeat_stack.pop()
                if remaining > 1:
                    self.repeat_stack.append((start_pc, remaining - 1))
                    self.pc = start_pc
                else:
                    self.running = False
                    print("Script completed")
            else:
                self.running = False
                print("Script completed")
            return

        # Execute current command
        cmd, args = self.commands[self.pc]

        try:
            if cmd == 'type':
                self.usb.type_text(args)

            elif cmd == 'press':
                self.usb.type_key(args)

            elif cmd == 'wait':
                self.wait_until = time.monotonic() + args

            elif cmd == 'repeat':
                # Push repeat context
                self.repeat_stack.append((self.pc + 1, args))

            elif cmd == 'click':
                self.usb.click_mouse(args)

            elif cmd == 'move':
                dx, dy = args
                self.usb.move_mouse(dx, dy)

            elif cmd == 'scroll':
                self.usb.scroll_mouse(args)

        except Exception as e:
            print(f"Script execution error: {e}")
            self.errors += 1
            self.running = False
            return

        # Advance program counter
        self.pc += 1

    def stats(self):
        """Get script engine statistics"""
        return {
            "running": self.running,
            "scripts_run": self.scripts_run,
            "errors": self.errors,
            "current_pc": self.pc if self.running else None,
            "total_commands": len(self.commands) if self.running else None,
        }


# Global script engine
script_engine = None

def init_script_engine(usb_manager):
    """Initialize global script engine"""
    global script_engine
    script_engine = ScriptEngine(usb_manager)
    return script_engine
