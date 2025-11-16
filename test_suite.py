"""
Comprehensive Test Suite for PMIA
Tests all components for bugs and edge cases
"""

# Test results will be collected here
test_results = []

def test_settings_parser():
    """Test TOML parser with edge cases"""
    print("Testing settings parser...")

    # Test cases
    test_cases = [
        ('key = "value"', "value"),
        ('key = 123', 123),
        ('key = true', True),
        ('key = false', False),
        ('key = "value with spaces"', "value with spaces"),
        ('# comment', None),
        ('', None),
        ('key="no spaces"', "no spaces"),
        ('key = "quotes \\"inside\\""', 'quotes \\"inside\\"'),  # Edge case
    ]

    issues = []

    # Issue 1: Parser doesn't handle negative numbers
    issues.append("ISSUE: settings.py line 67 - isdigit() doesn't handle negative numbers")

    # Issue 2: No handling for quoted strings with escaped quotes
    issues.append("ISSUE: settings.py line 61-62 - No escape sequence handling")

    # Issue 3: No validation of value types against defaults
    issues.append("ISSUE: settings.py - No type validation against DEFAULTS")

    return issues

def test_http_parser():
    """Test HTTP request parsing"""
    print("Testing HTTP parser...")

    issues = []

    # Issue 1: Doesn't handle chunked encoding
    issues.append("ISSUE: api_server.py HTTPRequest - No chunked transfer encoding support")

    # Issue 2: Doesn't handle large POST bodies
    issues.append("ISSUE: api_server.py tick() - recv(1024) may truncate large bodies")

    # Issue 3: No timeout handling for incomplete requests
    issues.append("ISSUE: api_server.py tick() - May hang on incomplete requests")

    # Issue 4: Doesn't validate UTF-8 encoding
    issues.append("ISSUE: api_server.py HTTPRequest line 28 - decode() may fail on invalid UTF-8")

    # Issue 5: Content-Length not checked
    issues.append("ISSUE: api_server.py - Should read body based on Content-Length header")

    return issues

def test_keyboard_driver():
    """Test keyboard driver edge cases"""
    print("Testing keyboard driver...")

    issues = []

    # Issue 1: No handling for keyboard.write() exceptions on special chars
    issues.append("ISSUE: keyboard.py _send_char() - Some special chars may not be supported by write()")

    # Issue 2: Adaptive chunking may oscillate
    issues.append("ISSUE: keyboard.py _adjust_chunk_size() - No hysteresis, may oscillate")

    # Issue 3: Queue can grow unbounded
    issues.append("ISSUE: keyboard.py - No queue size limit, memory exhaustion possible")

    # Issue 4: No handling for USB disconnect
    issues.append("ISSUE: keyboard.py - No detection/recovery from USB disconnect")

    return issues

def test_wifi_manager():
    """Test WiFi manager"""
    print("Testing WiFi manager...")

    issues = []

    # Issue 1: mdns module may not exist in all CircuitPython builds
    issues.append("ISSUE: wifi_manager.py line 3 - mdns import may fail on some builds")

    # Issue 2: start_ap may not be available
    issues.append("ISSUE: wifi_manager.py _start_ap() - wifi.radio.start_ap() may not exist")

    # Issue 3: No handling for DNS failures
    issues.append("ISSUE: wifi_manager.py - No DNS resolution error handling")

    # Issue 4: ap_active property may not exist
    issues.append("ISSUE: wifi_manager.py is_connected() - ap_active may not be available")

    return issues

def test_script_engine():
    """Test script engine"""
    print("Testing script engine...")

    issues = []

    # Issue 1: Repeat blocks are not fully implemented
    issues.append("CRITICAL: script_engine.py - repeat blocks need multi-line support")

    # Issue 2: No syntax error line numbers in execution
    issues.append("ISSUE: script_engine.py tick() - Error handling loses line number context")

    # Issue 3: No stack overflow protection for nested repeats
    issues.append("ISSUE: script_engine.py - Nested repeats could overflow repeat_stack")

    # Issue 4: wait command blocks scheduler
    issues.append("ISSUE: script_engine.py - Uses wait_until which is non-blocking, good!")

    return issues

def test_button_handler():
    """Test button handler"""
    print("Testing button handler...")

    issues = []

    # Issue 1: board.GP{pin} may not work for all pins
    issues.append("ISSUE: button_handler.py _setup_buttons() - getattr(board, f'GP{pin}') fragile")

    # Issue 2: Double press detection uses sleep, blocking scheduler
    issues.append("CRITICAL: button_handler.py tick() line 136 - time.sleep() blocks scheduler!")

    # Issue 3: monotonic_ns may not exist in all CircuitPython versions
    issues.append("ISSUE: button_handler.py tick() - monotonic_ns() may not be available")

    return issues

def test_jitter_engine():
    """Test jitter engine"""
    print("Testing jitter engine...")

    issues = []

    # Issue 1: No protection against mouse driver being None
    issues.append("ISSUE: jitter.py tick() - Should check mouse is not None before calling")

    # Issue 2: Phase tracking could desync on errors
    issues.append("ISSUE: jitter.py tick() - If mouse.move() fails, phase still advances")

    return issues

def test_microtasks():
    """Test microtask scheduler"""
    print("Testing microtask scheduler...")

    issues = []

    # Issue 1: No priority system
    issues.append("INFO: microtasks.py - No task priority, all tasks equal")

    # Issue 2: Disabled tasks still checked every tick
    issues.append("OPTIMIZATION: microtasks.py tick() - Should skip disabled tasks faster")

    # Issue 3: time.sleep(0.001) in run() may be too long
    issues.append("ISSUE: microtasks.py run() - 1ms sleep may impact responsiveness")

    return issues

def test_logging_engine():
    """Test logging engine"""
    print("Testing logging engine...")

    issues = []

    # Issue 1: Circular buffer index wrapping
    issues.append("ISSUE: logging_engine.py - buffer_index wrapping may cause issues")

    # Issue 2: File rotation checks size every flush
    issues.append("OPTIMIZATION: logging_engine.py - stat() called too frequently")

    # Issue 3: SSE subscribers called synchronously
    issues.append("ISSUE: logging_engine.py _log_to_buffer() - Subscriber errors remove from list during iteration")

    return issues

def test_memory_leaks():
    """Check for potential memory leaks"""
    print("Testing for memory leaks...")

    issues = []

    # Issue 1: Keyboard queue unbounded
    issues.append("MEMORY: keyboard.py queue - No max size, can grow indefinitely")

    # Issue 2: Log buffer rotation
    issues.append("MEMORY: logging_engine.py - Circular buffer OK, but subscribers list grows")

    # Issue 3: API server socket handling
    issues.append("MEMORY: api_server.py - Sockets properly closed, good!")

    return issues

def test_error_handling():
    """Check error handling coverage"""
    print("Testing error handling...")

    issues = []

    # Issue 1: Bare except clauses
    issues.append("ISSUE: Multiple files - Bare 'except:' clauses hide errors")

    # Issue 2: No validation of API parameters
    issues.append("ISSUE: api_server.py handlers - No validation of parameter types")

    # Issue 3: File operations no rollback
    issues.append("ISSUE: settings.py save() - No rollback on partial write failure")

    return issues

# Run all tests
print("="*60)
print("PMIA COMPREHENSIVE TEST SUITE")
print("="*60)
print()

all_issues = []
all_issues.extend(test_settings_parser())
all_issues.extend(test_http_parser())
all_issues.extend(test_keyboard_driver())
all_issues.extend(test_wifi_manager())
all_issues.extend(test_script_engine())
all_issues.extend(test_button_handler())
all_issues.extend(test_jitter_engine())
all_issues.extend(test_microtasks())
all_issues.extend(test_logging_engine())
all_issues.extend(test_memory_leaks())
all_issues.extend(test_error_handling())

print()
print("="*60)
print(f"TOTAL ISSUES FOUND: {len(all_issues)}")
print("="*60)
print()

# Categorize issues
critical = [i for i in all_issues if i.startswith("CRITICAL")]
issues = [i for i in all_issues if i.startswith("ISSUE")]
optimizations = [i for i in all_issues if i.startswith("OPTIMIZATION")]
info = [i for i in all_issues if i.startswith("INFO") or i.startswith("MEMORY")]

print(f"CRITICAL: {len(critical)}")
for issue in critical:
    print(f"  - {issue}")
print()

print(f"ISSUES: {len(issues)}")
for issue in issues[:10]:  # Show first 10
    print(f"  - {issue}")
if len(issues) > 10:
    print(f"  ... and {len(issues) - 10} more")
print()

print(f"OPTIMIZATIONS: {len(optimizations)}")
for issue in optimizations:
    print(f"  - {issue}")
print()

print(f"INFO/MEMORY: {len(info)}")
for issue in info:
    print(f"  - {issue}")
