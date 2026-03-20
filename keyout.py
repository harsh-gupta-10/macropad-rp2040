from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
import time
import json

# Initialize HID devices
keyboard = Keyboard(usb_hid.devices)

# Load configurations from JSON file
try:
    with open("keysfile.json", "r") as f:
        config = json.load(f)
    profiles_config = config.get("profiles", {})
    print(f"[INIT] JSON loaded successfully. Profiles: {list(profiles_config.keys())}")
    for p_idx, p_data in profiles_config.items():
        print(f"[INIT]   Profile {p_idx}: keys {list(p_data.keys())}")
except FileNotFoundError:
    print("[ERROR] keysfile.json not found!")
    profiles_config = {}
except Exception as e:
    print(f"[ERROR] Failed to load JSON: {e}")
    import traceback
    traceback.print_exc()
    profiles_config = {}

# Dictionary with key configurations: key_index -> {name, key, function}
profiles = {}


def _is_text_action(key_config):
    """Return True when config represents a text typing action."""
    # Explicit action field takes priority
    if key_config.get("action") == "text_input":
        return True
    # If has text_content, it's a text action
    if "text_content" in key_config:
        return True
    # Check if key field contains text_input (legacy support)
    key_value = key_config.get("key")
    if isinstance(key_value, list) and "text_input" in key_value:
        print(f"[WARN] Found 'text_input' in key field - should use action field instead")
        return True
    return False


def _normalized_key_list(key_value):
    """Normalize stored key token(s) into a list."""
    if isinstance(key_value, list):
        return key_value
    if isinstance(key_value, str):
        return [key_value]
    return []


def _is_software_action(key_config):
    if key_config.get("action") == "software":
        return bool(key_config.get("software"))
    return bool(key_config.get("software"))

def execute_combination(*keys):
    """Simulate pressing a combination of keys."""
    key_dict = {
    "windows": Keycode.WINDOWS,
    # Letters
    "a": Keycode.A, "b": Keycode.B, "c": Keycode.C, "d": Keycode.D,
    "e": Keycode.E, "f": Keycode.F, "g": Keycode.G, "h": Keycode.H,
    "i": Keycode.I, "j": Keycode.J, "k": Keycode.K, "l": Keycode.L,
    "m": Keycode.M, "n": Keycode.N, "o": Keycode.O, "p": Keycode.P,
    "q": Keycode.Q, "r": Keycode.R, "s": Keycode.S, "t": Keycode.T,
    "u": Keycode.U, "v": Keycode.V, "w": Keycode.W, "x": Keycode.X,
    "y": Keycode.Y, "z": Keycode.Z,

    # Numbers
    "0": Keycode.ZERO, "1": Keycode.ONE, "2": Keycode.TWO, "3": Keycode.THREE,
    "4": Keycode.FOUR, "5": Keycode.FIVE, "6": Keycode.SIX, "7": Keycode.SEVEN,
    "8": Keycode.EIGHT, "9": Keycode.NINE,

    # Special characters
    "backslash": Keycode.BACKSLASH, "space": Keycode.SPACEBAR, "enter": Keycode.ENTER,
    "esc": Keycode.ESCAPE, "backspace": Keycode.BACKSPACE, "tab": Keycode.TAB,
    "shift": Keycode.SHIFT, "ctrl": Keycode.CONTROL, "alt": Keycode.ALT,
    "up": Keycode.UP_ARROW, "down": Keycode.DOWN_ARROW, "left": Keycode.LEFT_ARROW,
    "right": Keycode.RIGHT_ARROW, "home": Keycode.HOME, "end": Keycode.END,
    "pageup": Keycode.PAGE_UP, "pagedown": Keycode.PAGE_DOWN, "insert": Keycode.INSERT,
    "delete": Keycode.DELETE,"print_screen":Keycode.PRINT_SCREEN,

    # Function Keys
    "f1": Keycode.F1, "f2": Keycode.F2, "f3": Keycode.F3, "f4": Keycode.F4,
    "f5": Keycode.F5, "f6": Keycode.F6, "f7": Keycode.F7, "f8": Keycode.F8,
    "f9": Keycode.F9, "f10": Keycode.F10, "f11": Keycode.F11, "f12": Keycode.F12,
    "f13": Keycode.F13, "f14": Keycode.F14, "f15": Keycode.F15, "f16": Keycode.F16,
    "f17": Keycode.F17, "f18": Keycode.F18, "f19": Keycode.F19, "f20": Keycode.F20,
    "f21": Keycode.F21, "f22": Keycode.F22, "f23": Keycode.F23, "f24": Keycode.F24,

    # Punctuation and symbols
    "comma": Keycode.COMMA, "period": Keycode.PERIOD, "slash": Keycode.FORWARD_SLASH,
    "semicolon": Keycode.SEMICOLON, "quote": Keycode.QUOTE, "left_bracket": Keycode.LEFT_BRACKET,
    "right_bracket": Keycode.RIGHT_BRACKET, "minus": Keycode.MINUS, "equal": Keycode.EQUALS
    }

    try:
        keys_to_press = [key_dict[key] for key in keys]
        print(f"[COMBO] Pressing keys: {keys} -> {keys_to_press}")
        keyboard.press(*keys_to_press)
        time.sleep(0.1)
        keyboard.release(*keys_to_press)
        print(f"[COMBO] Released successfully")
    except KeyError as e:
        print(f"[ERROR] Unsupported key in combination: {e}")
        print(f"[ERROR] Tried to map: {keys}")
    except Exception as e:
        print(f"[ERROR] execute_combination failed: {e}")
        import traceback
        traceback.print_exc()

def open_software(software_name):
    """Open a specific software by typing its name and pressing Enter."""
    keyboard.press(Keycode.WINDOWS)
    time.sleep(0.2)
    keyboard.release(Keycode.WINDOWS)
    time.sleep(0.5)  # Wait for the search bar
    type_string(software_name)  # Type the software name
    time.sleep(0.5)
    keyboard.press(Keycode.ENTER)
    keyboard.release(Keycode.ENTER)


def _tap_key(keycode, use_shift=False):
    if use_shift:
        keyboard.press(Keycode.SHIFT)
    keyboard.press(keycode)
    time.sleep(0.01)  # Reduced from 0.02
    keyboard.release(keycode)
    if use_shift:
        keyboard.release(Keycode.SHIFT)


def type_string_simple(text):
    """Type text using simple, reliable character-by-character method - optimized for speed."""
    for char in text:
        if char == "\n":
            keyboard.press(Keycode.ENTER)
            keyboard.release(Keycode.ENTER)
            time.sleep(0.02)  # Reduced from 0.05
        elif char == "\t":
            keyboard.press(Keycode.TAB)
            keyboard.release(Keycode.TAB)
            time.sleep(0.02)  # Reduced from 0.05
        elif char == " ":
            keyboard.press(Keycode.SPACEBAR)
            keyboard.release(Keycode.SPACEBAR)
            time.sleep(0.02)  # Reduced from 0.05
        else:
            # Try to map character to key+shift combination
            key_result = _char_to_key(char)
            if key_result:
                keycode, use_shift = key_result
                if use_shift:
                    keyboard.press(Keycode.SHIFT)
                keyboard.press(keycode)
                time.sleep(0.01)  # Reduced from 0.02
                keyboard.release(keycode)
                if use_shift:
                    keyboard.release(Keycode.SHIFT)
            else:
                print(f"[TYPING] Skipping unsupported: {char}")
        time.sleep(0.03)  # Reduced from 0.08 - delay between characters


def _char_to_key(char):
    # Letters
    if "a" <= char <= "z":
        return getattr(Keycode, char.upper()), False
    if "A" <= char <= "Z":
        return getattr(Keycode, char), True

    # Digits
    digit_map = {
        "0": Keycode.ZERO,
        "1": Keycode.ONE,
        "2": Keycode.TWO,
        "3": Keycode.THREE,
        "4": Keycode.FOUR,
        "5": Keycode.FIVE,
        "6": Keycode.SIX,
        "7": Keycode.SEVEN,
        "8": Keycode.EIGHT,
        "9": Keycode.NINE,
    }
    if char in digit_map:
        return digit_map[char], False

    # Common symbols on US layout
    symbol_map = {
        " ": (Keycode.SPACEBAR, False),
        "-": (Keycode.MINUS, False),
        "_": (Keycode.MINUS, True),
        "=": (Keycode.EQUALS, False),
        "+": (Keycode.EQUALS, True),
        "[": (Keycode.LEFT_BRACKET, False),
        "{": (Keycode.LEFT_BRACKET, True),
        "]": (Keycode.RIGHT_BRACKET, False),
        "}": (Keycode.RIGHT_BRACKET, True),
        "\\": (Keycode.BACKSLASH, False),
        "|": (Keycode.BACKSLASH, True),
        ";": (Keycode.SEMICOLON, False),
        ":": (Keycode.SEMICOLON, True),
        "'": (Keycode.QUOTE, False),
        '"': (Keycode.QUOTE, True),
        ",": (Keycode.COMMA, False),
        "<": (Keycode.COMMA, True),
        ".": (Keycode.PERIOD, False),
        ">": (Keycode.PERIOD, True),
        "/": (Keycode.FORWARD_SLASH, False),
        "?": (Keycode.FORWARD_SLASH, True),
        "!": (Keycode.ONE, True),
        "@": (Keycode.TWO, True),
        "#": (Keycode.THREE, True),
        "$": (Keycode.FOUR, True),
        "%": (Keycode.FIVE, True),
        "^": (Keycode.SIX, True),
        "&": (Keycode.SEVEN, True),
        "*": (Keycode.EIGHT, True),
        "(": (Keycode.NINE, True),
        ")": (Keycode.ZERO, True),
    }

    # Add optional keys only when present in this firmware build.
    grave = getattr(Keycode, "GRAVE_ACCENT", None)
    if grave is not None:
        symbol_map["`"] = (grave, False)
        symbol_map["~"] = (grave, True)

    return symbol_map.get(char)

def type_string(text):
    """Simulate typing a string character by character (legacy - slower version)."""
    for char in text:
        if char == "\n":  # Newline
            keyboard.press(Keycode.ENTER)
            keyboard.release(Keycode.ENTER)
        elif char == "\t":  # Tab
            keyboard.press(Keycode.TAB)
            keyboard.release(Keycode.TAB)
        else:
            key_result = _char_to_key(char)
            if key_result:
                keycode, use_shift = key_result
                _tap_key(keycode, use_shift)
            else:
                print(f"Unsupported character: {char}")
        time.sleep(0.03)  # Reduced from 0.05

def type_text_content(text_content, text_type="single", press_enter=False):
    """Type the content of a text configuration.
    
    Args:
        text_content (str): The text to type
        text_type (str): Type of text input
            - "single": Type the text as-is
            - "line-by-line": Type each line with a pause between
            - "paragraph": Type with proper paragraph formatting
    """
    print(f"[TYPING] Starting: text_type={text_type}, len={len(text_content) if text_content else 0}")
    
    if not text_content:
        print("[TYPING] No text content to type")
        return
    
    if text_type == "line-by-line":
        lines = text_content.splitlines()
        for i, line in enumerate(lines):
            print(f"[TYPING] Line {i+1}/{len(lines)}")
            type_string_simple(line)
            if i < len(lines) - 1:
                keyboard.press(Keycode.ENTER)
                keyboard.release(Keycode.ENTER)
                time.sleep(0.3)
    elif text_type == "paragraph":
        paragraphs = text_content.split('\n\n')
        for i, para in enumerate(paragraphs):
            print(f"[TYPING] Paragraph {i+1}/{len(paragraphs)}")
            type_string_simple(para)
            if i < len(paragraphs) - 1:
                keyboard.press(Keycode.ENTER)
                keyboard.release(Keycode.ENTER)
                time.sleep(0.1)
                keyboard.press(Keycode.ENTER)
                keyboard.release(Keycode.ENTER)
                time.sleep(0.3)
    else:  # Default to "single"
        print("[TYPING] Single mode")
        type_string_simple(text_content)

    if press_enter:
        print("[TYPING] Pressing ENTER at end")
        keyboard.press(Keycode.ENTER)
        keyboard.release(Keycode.ENTER)
    
    print("[TYPING] Complete")


def _execute_from_config(key_config):
    """Execute one key action directly from raw config payload."""
    if not isinstance(key_config, dict):
        print("Invalid key config")
        return

    if _is_text_action(key_config):
        text_content = key_config.get("text_content", "")
        text_type = key_config.get("text_type", "single")
        text_press_enter = key_config.get("text_press_enter", True)
        type_text_content(text_content, text_type, text_press_enter)
        return

    if _is_software_action(key_config):
        open_software(key_config.get("software", ""))
        return

    key_tokens = _normalized_key_list(key_config.get("key"))
    if key_tokens:
        execute_combination(*key_tokens)
        return

    print("Key not configured")

# Generate profiles with functions from JSON configuration
print("[INIT] Building profiles from JSON config...")
for profile_idx, profile_data in profiles_config.items():
    profile_idx = int(profile_idx)  # Convert string index to integer
    profiles[profile_idx] = {}
    print(f"[INIT] Building profile {profile_idx}...")
    
    for key_idx, key_config in profile_data.items():
        key_idx = int(key_idx)  # Convert string index to integer
        if not isinstance(key_config, dict):
            print(f"[INIT]   Key {key_idx}: SKIP - not a dict")
            continue

        key_name = key_config.get("name", f"Key {key_idx}")
        key_tokens = _normalized_key_list(key_config.get("key"))
        
        # Create the appropriate function based on configuration
        if _is_text_action(key_config):
            # This is a text input action
            if "text_content" in key_config:
                text_content = key_config["text_content"]
                text_type = key_config.get("text_type", "single")
                text_press_enter = key_config.get("text_press_enter", True)
                profiles[profile_idx][key_idx] = {
                    "name": key_name,
                    "key": key_tokens,
                    "function": lambda t=text_content, ty=text_type, pe=text_press_enter: type_text_content(t, ty, pe)
                }
                print(f"[INIT]   Key {key_idx} ({key_name}): TEXT_INPUT mode")
            else:
                profiles[profile_idx][key_idx] = {
                    "name": key_name,
                    "key": key_tokens,
                    "function": lambda: print("No text content defined")
                }
                print(f"[INIT]   Key {key_idx} ({key_name}): TEXT_INPUT but no content")
        elif _is_software_action(key_config):
            # This is a software opening action
            software_name = key_config.get("software", "")
            profiles[profile_idx][key_idx] = {
                "name": key_name,
                "key": key_tokens,
                "function": lambda s=software_name: open_software(s)
            }
            print(f"[INIT]   Key {key_idx} ({key_name}): SOFTWARE mode ({software_name})")
        elif key_tokens:
            # This is a key combination action
            key_combo = key_tokens
            profiles[profile_idx][key_idx] = {
                "name": key_name,
                "key": key_combo,
                "function": lambda k=key_combo: execute_combination(*k)
            }
            print(f"[INIT]   Key {key_idx} ({key_name}): COMBO mode ({key_combo})")
        else:
            profiles[profile_idx][key_idx] = {
                "name": key_name,
                "key": [],
                "function": lambda: print("Key not configured")
            }
            print(f"[INIT]   Key {key_idx} ({key_name}): NOT CONFIGURED")

print(f"[INIT] Profile building complete. Total profiles: {len(profiles)}")

# Function to trigger key action based on key_index
def execute_action(key_index, profile_index=0):
    try:
        print(f"\n[KEY PRESS] key={key_index}, profile={profile_index}")
        
        # Runtime-first path: execute directly from JSON-derived config.
        profile_cfg = profiles_config.get(str(profile_index), {})
        if not profile_cfg:
            print(f"[ACTION] Profile {profile_index} not found in profiles_config")
            return
        
        key_cfg = profile_cfg.get(str(key_index))
        if key_cfg is not None:
            print(f"[ACTION] Found in runtime config, executing...")
            _execute_from_config(key_cfg)
            return
        
        print(f"[ACTION] Key {key_index} not in profile {profile_index} runtime config")

        # Fallback to prebuilt map if runtime entry is missing.
        profile = profiles.get(profile_index, {})
        action = profile.get(key_index)
        if action:
            print(f"[ACTION] Found in prebuilt map, executing...")
            action["function"]()
            return

        print(f"[WARNING] Missing action for key {key_index} in profile {profile_index}")
    except KeyError as e:
        print(f"[ERROR] KeyError for Key {key_index} in Profile {profile_index}: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error for Key {key_index} in Profile {profile_index}: {e}")
        import traceback
        traceback.print_exc()