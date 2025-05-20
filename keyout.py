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
    profiles_config = config["profiles"]
except Exception as e:
    print(f"Error loading configuration: {e}")
    # Fallback to default configuration if file loading fails
    profiles_config = {}

# Dictionary with key configurations: key_index -> {name, key, function}
profiles = {}

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
        keyboard.press(*keys_to_press)
        time.sleep(0.1)
        keyboard.release(*keys_to_press)
    except KeyError as e:
        print(f"Unsupported key: {e}")

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

def type_string(text):
    """Simulate typing a string character by character."""
    for char in text:
        if char.isupper():  # Uppercase letters
            keyboard.press(Keycode.SHIFT, getattr(Keycode, char.upper()))
            keyboard.release(Keycode.SHIFT, getattr(Keycode, char.upper()))
        elif char.islower():  # Lowercase letters
            keyboard.press(getattr(Keycode, char.upper()))
            keyboard.release(getattr(Keycode, char.upper()))
        elif char == " ":  # Space
            keyboard.press(Keycode.SPACE)
            keyboard.release(Keycode.SPACE)
        elif char == "\n":  # Newline
            keyboard.press(Keycode.ENTER)
            keyboard.release(Keycode.ENTER)
        elif char == "\t":  # Tab
            keyboard.press(Keycode.TAB)
            keyboard.release(Keycode.TAB)
        elif char.isdigit():  # Numbers
            key_attr = f"KEYCODE_{char}"
            if hasattr(Keycode, key_attr):
                keyboard.press(getattr(Keycode, key_attr))
                keyboard.release(getattr(Keycode, key_attr))
            else:
                # Fallback for numbers
                num_keys = {
                    "0": Keycode.ZERO, "1": Keycode.ONE, "2": Keycode.TWO, "3": Keycode.THREE,
                    "4": Keycode.FOUR, "5": Keycode.FIVE, "6": Keycode.SIX, "7": Keycode.SEVEN,
                    "8": Keycode.EIGHT, "9": Keycode.NINE
                }
                if char in num_keys:
                    keyboard.press(num_keys[char])
                    keyboard.release(num_keys[char])
        elif char in ",.;:-_=+()[]{}!@#$%^&*?/\\":  # Common punctuation
            # Map of special characters to their key combinations
            punctuation_map = {
                ",": (None, Keycode.COMMA),
                ".": (None, Keycode.PERIOD),
                ";": (None, Keycode.SEMICOLON),
                ":": (Keycode.SHIFT, Keycode.SEMICOLON),
                "-": (None, Keycode.MINUS),
                "_": (Keycode.SHIFT, Keycode.MINUS),
                "=": (None, Keycode.EQUALS),
                "+": (Keycode.SHIFT, Keycode.EQUALS),
                "(": (Keycode.SHIFT, Keycode.NINE),
                ")": (Keycode.SHIFT, Keycode.ZERO),
                "[": (None, Keycode.LEFT_BRACKET),
                "]": (None, Keycode.RIGHT_BRACKET),
                "{": (Keycode.SHIFT, Keycode.LEFT_BRACKET),
                "}": (Keycode.SHIFT, Keycode.RIGHT_BRACKET),
                "!": (Keycode.SHIFT, Keycode.ONE),
                "@": (Keycode.SHIFT, Keycode.TWO),
                "#": (Keycode.SHIFT, Keycode.THREE),
                "$": (Keycode.SHIFT, Keycode.FOUR),
                "%": (Keycode.SHIFT, Keycode.FIVE),
                "^": (Keycode.SHIFT, Keycode.SIX),
                "&": (Keycode.SHIFT, Keycode.SEVEN),
                "*": (Keycode.SHIFT, Keycode.EIGHT),
                "?": (Keycode.SHIFT, Keycode.FORWARD_SLASH),
                "/": (None, Keycode.FORWARD_SLASH),
                "\\": (None, Keycode.BACKSLASH)
            }
            
            if char in punctuation_map:
                modifier, keycode = punctuation_map[char]
                if modifier:
                    keyboard.press(modifier, keycode)
                    keyboard.release(modifier, keycode)
                else:
                    keyboard.press(keycode)
                    keyboard.release(keycode)
            else:
                print(f"Unsupported punctuation: {char}")
        else:
            # Handle unsupported characters
            print(f"Unsupported character: {char}")
        time.sleep(0.05)  # Add a short delay between characters

def type_text_content(text_content, text_type="single"):
    """Type the content of a text configuration.
    
    Args:
        text_content (str): The text to type
        text_type (str): Type of text input
            - "single": Type the text as-is
            - "line-by-line": Type each line with a pause between
            - "paragraph": Type with proper paragraph formatting
    """
    if text_type == "line-by-line":
        lines = text_content.splitlines()
        for i, line in enumerate(lines):
            type_string(line)
            if i < len(lines) - 1:  # Don't add newline after last line
                keyboard.press(Keycode.ENTER)
                keyboard.release(Keycode.ENTER)
                time.sleep(0.2)  # Pause between lines
    elif text_type == "paragraph":
        # Add two newlines between paragraphs
        paragraphs = text_content.split('\n\n')
        for i, para in enumerate(paragraphs):
            type_string(para)
            if i < len(paragraphs) - 1:  # Don't add newline after last paragraph
                keyboard.press(Keycode.ENTER)
                keyboard.release(Keycode.ENTER)
                time.sleep(0.1)
                keyboard.press(Keycode.ENTER)
                keyboard.release(Keycode.ENTER)
                time.sleep(0.2)
    else:  # Default to "single"
        type_string(text_content)

# Generate profiles with functions from JSON configuration
for profile_idx, profile_data in profiles_config.items():
    profile_idx = int(profile_idx)  # Convert string index to integer
    profiles[profile_idx] = {}
    
    for key_idx, key_config in profile_data.items():
        key_idx = int(key_idx)  # Convert string index to integer
        
        # Create the appropriate function based on configuration
        if "software" in key_config:
            # This is a software opening action
            software_name = key_config["software"]
            profiles[profile_idx][key_idx] = {
                "name": key_config["name"],
                "key": key_config["key"],
                "function": lambda s=software_name: open_software(s)
            }
        elif "key" in key_config and "text_input" in key_config["key"]:
            # This is a text input action
            if "text_content" in key_config:
                text_content = key_config["text_content"]
                text_type = key_config.get("text_type", "single")
                profiles[profile_idx][key_idx] = {
                    "name": key_config["name"],
                    "key": key_config["key"],
                    "function": lambda t=text_content, ty=text_type: type_text_content(t, ty)
                }
            else:
                profiles[profile_idx][key_idx] = {
                    "name": key_config["name"],
                    "key": key_config["key"],
                    "function": lambda: print("No text content defined")
                }
        else:
            # This is a key combination action
            key_combo = key_config["key"]
            profiles[profile_idx][key_idx] = {
                "name": key_config["name"],
                "key": key_combo,
                "function": lambda k=key_combo: execute_combination(*k)
            }

# Function to trigger key action based on key_index
def execute_action(key_index, profile_index=0):
    try:
        profiles[profile_index][key_index]["function"]()
    except KeyError as e:
        print(f"Error executing action for Key {key_index} in Profile {profile_index}: {e}")
    except Exception as e:
        print(f"Unexpected error for Key {key_index} in Profile {profile_index}: {e}")