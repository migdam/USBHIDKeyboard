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
    """Parses macro DSL with multi-line block support"""

    @staticmethod
    def parse(script_text):
        """
        Parse script into command list with repeat block support

        Returns: List of (command, args, line_no) tuples
        """
        commands = []
        lines = script_text.strip().split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            line_no = i + 1

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue

            try:
                # Check for repeat block
                if line.startswith('repeat '):
                    # Parse repeat count
                    if '{' in line:
                        parts = line.split('{')
                        count = int(parts[0].replace('repeat', '').strip())
                    else:
                        count = int(line.replace('repeat', '').strip())

                    # Find matching closing brace
                    block_lines = []
                    brace_count = 1 if '{' in line else 0
                    i += 1

                    # Look for opening brace if not on same line
                    if brace_count == 0:
                        while i < len(lines):
                            if lines[i].strip() == '{':
                                brace_count = 1
                                i += 1
                                break
                            i += 1

                    # Collect block contents
                    while i < len(lines) and brace_count > 0:
                        block_line = lines[i].strip()
                        if block_line == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                break
                        elif '{' in block_line:
                            brace_count += 1

                        if brace_count > 0:
                            block_lines.append(block_line)
                        i += 1

                    # Parse block contents into sub-commands
                    if block_lines:
                        # Add repeat start marker
                        commands.append(('repeat_start', count, line_no))

                        # Parse each line in block
                        for block_line in block_lines:
                            if block_line and not block_line.startswith('#'):
                                cmd = ScriptParser._parse_line(block_line)
                                if cmd:
                                    commands.append((cmd[0], cmd[1], line_no))

                        # Add repeat end marker
                        commands.append(('repeat_end', None, line_no))
                    else:
                        # Empty repeat block
                        commands.append(('repeat_start', count, line_no))
                        commands.append(('repeat_end', None, line_no))
                else:
                    # Regular command
                    cmd = ScriptParser._parse_line(line)
                    if cmd:
                        commands.append((cmd[0], cmd[1], line_no))

            except Exception as e:
                raise SyntaxError(f"Line {line_no}: {e}")

            i += 1

        return commands

    @staticmethod
    def _parse_line(line):
        """Parse a single command line"""
        # Handle closing brace (for block end detection)
        if line == '}':
            return None

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

        # click button
        elif line.startswith('click '):
            button = line[6:].strip()
            return ('click', button)

        # move dx dy
        elif line.startswith('move '):
            parts = line[5:].strip().split()
            if len(parts) < 2:
                raise SyntaxError("move requires dx and dy")
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
            self.running = False
            print("Script completed")
            return

        # Execute current command
        cmd_tuple = self.commands[self.pc]
        cmd = cmd_tuple[0]
        args = cmd_tuple[1]
        line_no = cmd_tuple[2] if len(cmd_tuple) > 2 else 0

        try:
            if cmd == 'type':
                self.usb.type_text(args)

            elif cmd == 'press':
                self.usb.type_key(args)

            elif cmd == 'wait':
                self.wait_until = time.monotonic() + args

            elif cmd == 'repeat_start':
                # Mark start of repeat block
                # args = count
                self.repeat_stack.append({
                    'start_pc': self.pc + 1,
                    'remaining': args,
                    'line_no': line_no
                })

            elif cmd == 'repeat_end':
                # Check if we should repeat
                if self.repeat_stack:
                    context = self.repeat_stack[-1]
                    if context['remaining'] > 1:
                        # Repeat again
                        context['remaining'] -= 1
                        self.pc = context['start_pc'] - 1  # Will be incremented below
                    else:
                        # Done repeating
                        self.repeat_stack.pop()

            elif cmd == 'click':
                self.usb.click_mouse(args)

            elif cmd == 'move':
                dx, dy = args
                self.usb.move_mouse(dx, dy)

            elif cmd == 'scroll':
                self.usb.scroll_mouse(args)

        except Exception as e:
            print(f"Script execution error at line {line_no}: {e}")
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
