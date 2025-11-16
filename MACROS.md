# Macro Scripting Guide

## Overview

The Pico Multi-Input Agent includes a simple DSL (Domain Specific Language) for creating automation macros.

Scripts are stored in `/scripts/` directory as `.txt` files.

## Syntax

### Comments

Lines starting with `#` are comments:

```
# This is a comment
type "Hello"  # This is also a comment
```

### Commands

#### type "text"

Type text via USB keyboard:

```
type "Hello, World!"
type "Multiple lines\nare supported"
```

#### press KEY

Press a special key:

```
press ENTER
press TAB
press ESC
```

**Available keys:**
- ENTER, TAB, ESC
- BACKSPACE, DELETE
- UP, DOWN, LEFT, RIGHT
- HOME, END, PAGE_UP, PAGE_DOWN
- F1, F2, ..., F12
- CTRL, ALT, SHIFT, GUI (Windows/Command)

#### wait milliseconds

Wait for specified time:

```
wait 1000  # Wait 1 second
wait 500   # Wait 0.5 seconds
```

#### repeat N { ... }

Repeat commands (simplified - single line per block):

```
repeat 5 {
    type "Loop iteration"
    press ENTER
    wait 500
}
```

**Note:** Full multi-line blocks require parsing enhancement.

#### click button

Click mouse button:

```
click left
click right
click middle
```

#### move dx dy

Move mouse cursor (relative):

```
move 100 0    # Move 100px right
move 0 100    # Move 100px down
move -50 -50  # Move 50px left and up
```

#### scroll amount

Scroll mouse wheel:

```
scroll 5   # Scroll up
scroll -5  # Scroll down
```

## Examples

### Hello World

```
# Simple hello world
type "Hello, World!"
press ENTER
```

### Open Application (Windows)

```
# Open Calculator
press GUI
wait 500
type "calc"
wait 200
press ENTER
```

### Navigation Test

```
# Test arrow keys
press DOWN
press DOWN
press RIGHT
press ENTER
```

### Mouse Square

```
# Draw a square
move 100 0
wait 500
move 0 100
wait 500
move -100 0
wait 500
move 0 -100
```

### Automated Form Filling

```
# Fill a form
type "John Doe"
press TAB
wait 200

type "john@example.com"
press TAB
wait 200

type "555-1234"
press TAB
wait 200

press ENTER
```

### Loop Example

```
# Type numbers 1-10
repeat 10 {
    type "Number"
    press ENTER
    wait 100
}
```

## Creating Your Own Macros

1. Create a new `.txt` file in `/scripts/` directory
2. Write your macro using the DSL syntax
3. Save the file
4. Access via Web UI or API:
   - Web UI: Macros panel → Refresh → Run
   - API: `POST /api/macro/run {"script": "your_macro"}`
   - Python: `client.run_macro("your_macro")`

## Best Practices

1. **Add comments** - Explain what your macro does
2. **Use waits** - Give applications time to respond
3. **Test incrementally** - Start simple, add complexity gradually
4. **Handle errors** - Consider what happens if target app isn't ready
5. **Keep it simple** - Complex logic is better in Python client

## Limitations

- No variables or conditionals
- No error handling
- No loops with dynamic counts
- Single-line repeat blocks only
- No file operations
- No network requests

For complex automation, use the Python client library instead.

## Running Macros

### Via Web UI

1. Open `http://pico.local`
2. Go to Macros panel
3. Click "Preview" to view script
4. Click "Run" to execute

### Via API

```bash
curl -X POST http://pico.local/api/macro/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"script": "hello_world"}'
```

### Via Python

```python
from pico_client import PicoClient

client = PicoClient("pico.local", api_key="your-key")
client.run_macro("hello_world")
```

### Via Hardware Button

Configure in `settings.toml`:

```toml
button1_script = "your_macro"
```

Press button 1 to run the macro.

## Advanced Tips

### Timing Considerations

- Default typing delay: 10ms per character
- Adjust via `settings.toml`: `typing_delay = 20`
- Add `wait` commands between actions
- Some applications need more time to respond

### Special Characters

All ASCII characters are supported:
```
type "Special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/"
```

### Keyboard Shortcuts

Combine with press commands:
```
press CTRL
type "c"
press CTRL
wait 100
press CTRL
type "v"
press CTRL
```

**Note:** Full combo support (e.g., `CTRL+C`) requires keyboard driver enhancement.

### Mouse Precision

- Mouse moves are relative (delta X, delta Y)
- Range: -127 to +127 pixels per move
- For larger movements, use multiple `move` commands
- Consider `wait` between moves for accuracy

## Troubleshooting

### Macro not found

- Check filename has `.txt` extension
- Verify file is in `/scripts/` directory
- Refresh macro list in Web UI

### Commands not executing

- Check syntax (quotes, spacing)
- Verify target application has focus
- Add more `wait` commands
- Check USB HID is working

### Unexpected behavior

- View logs in Web UI (Logs panel)
- Check script execution status
- Test commands individually first
- Verify target OS keyboard layout matches

## Future Enhancements

Planned features:
- Variables and conditionals
- Multi-line repeat blocks
- Error handling and recovery
- Importing other scripts
- Debugging mode with step-through
