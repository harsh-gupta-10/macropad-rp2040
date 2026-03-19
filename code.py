import time
import json
import digitalio
import board
import busio
import usb_hid
import displayio
from adafruit_displayio_sh1106 import SH1106
from rotaryio import IncrementalEncoder
import terminalio
from adafruit_display_text import label
from digitalio import Direction, Pull
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from keyout import execute_action

cc = ConsumerControl(usb_hid.devices)

encoder1 = IncrementalEncoder(board.GP14, board.GP15)
last_position_encoder1 = None

class SoftwareEncoder:
    def __init__(self, pinA, pinB):
        self.a = digitalio.DigitalInOut(pinA)
        self.b = digitalio.DigitalInOut(pinB)
        self.a.direction = digitalio.Direction.INPUT
        self.a.pull = digitalio.Pull.UP
        self.b.direction = digitalio.Direction.INPUT
        self.b.pull = digitalio.Pull.UP
        self.position = 0
        self._last_state = (self.a.value, self.b.value)

    def update(self):
        current_state = (self.a.value, self.b.value)
        if current_state != self._last_state:
            if self._last_state[0] != current_state[0]:
                if current_state[0] == current_state[1]:
                    self.position -= 1
                else:
                    self.position += 1
            else:
                if current_state[0] == current_state[1]:
                    self.position += 1
                else:
                    self.position -= 1
            self._last_state = current_state

softEncoder2 = SoftwareEncoder(board.GP18, board.GP19)
last_softPos2 = None

encoder1_button = digitalio.DigitalInOut(board.GP17)
encoder1_button.direction = Direction.INPUT
encoder1_button.pull = Pull.UP

encoder2_button = digitalio.DigitalInOut(board.GP20)
encoder2_button.direction = digitalio.Direction.INPUT
encoder2_button.pull = digitalio.Pull.UP

volume_hold_start = None
is_holding_volume_button = False
last_volume_button_state = True

display_hold_start = None
is_holding_display_button = False
last_display_button_state = True

last_profile_switch_time = 0
last_key_press_time = 0
debounce_delay = 0.2

displayio.release_displays()
i2c = busio.I2C(board.GP9, board.GP8)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SH1106(display_bus, width=130, height=64)

def setup_button(pin):
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    return button
def debounce_check(last_time, delay=0.5):
    return time.monotonic() - last_time > delay
last_mic_action_time = 0
last_encoder2_action_time = 0

mute_mic = setup_button(board.GP0)

cols = [digitalio.DigitalInOut(pin) for pin in [board.GP1, board.GP2, board.GP3]]
rows = [digitalio.DigitalInOut(pin) for pin in [board.GP4, board.GP13, board.GP6]]

for row in rows:
    row.direction = digitalio.Direction.OUTPUT
    row.value = False
for col in cols:
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.DOWN

key_mapping = {
    (0, 0): 1, (0, 1): 4, (0, 2): 7,
    (1, 0): 3, (1, 1): 6, (1, 2): 9,
    (2, 0): 2, (2, 1): 5, (2, 2): 8,
}

image_files = [
    "/img/youtube-logo-bmp.bmp",
    "/img/vscode-logo-bmp.bmp",
    "/img/obs-logo-bmp.bmp",
    "/img/volt-logo-bmp.bmp",
    "/img/windows-logo-bmp.bmp",
    "/img/photoshop-logo-bmp.bmp",
]

selected_index = 0

SPECIAL_DEFAULTS = {
    "volume_encoder_left": {"name": "Volume Down", "key": ["media_volume_down"]},
    "volume_encoder_right": {"name": "Volume Up", "key": ["media_volume_up"]},
    "volume_encoder_click": {"name": "Play/Pause", "key": ["media_play_pause"]},
    "volume_encoder_hold": {"name": "Mute", "key": ["media_mute"]},
    "display_encoder_left": {"name": "Prev Profile", "action": "profile_prev"},
    "display_encoder_right": {"name": "Next Profile", "action": "profile_next"},
    "display_encoder_click": {"name": "Switch Profile", "action": "profile_next"},
    "display_encoder_hold": {"name": "No Action", "action": "none"},
    "mic_key": {"name": "Mic Toggle", "key": ["f13"]},
}


def load_special_actions():
    """Load editable special actions with safe defaults."""
    try:
        with open("special-keyout.json", "r") as f:
            data = json.load(f)
        actions = data.get("special_keys", {})
    except Exception as e:
        print(f"special-keyout.json load error: {e}")
        actions = {}

    merged = {}
    for action_id, default_entry in SPECIAL_DEFAULTS.items():
        merged[action_id] = default_entry.copy()
        if action_id in actions and isinstance(actions[action_id], dict):
            merged[action_id].update(actions[action_id])
    return merged


def normalize_token(token):
    return str(token).strip().lower().replace("-", "_").replace(" ", "_")


def token_to_keycode(token):
    token = normalize_token(token)
    key_map = {
        "ctrl": Keycode.CONTROL,
        "control": Keycode.CONTROL,
        "alt": Keycode.ALT,
        "shift": Keycode.SHIFT,
        "windows": Keycode.WINDOWS,
        "win": Keycode.WINDOWS,
        "esc": Keycode.ESCAPE,
        "escape": Keycode.ESCAPE,
        "tab": Keycode.TAB,
        "space": Keycode.SPACE,
        "spacebar": Keycode.SPACE,
        "enter": Keycode.ENTER,
        "backspace": Keycode.BACKSPACE,
        "up": Keycode.UP_ARROW,
        "down": Keycode.DOWN_ARROW,
        "left": Keycode.LEFT_ARROW,
        "right": Keycode.RIGHT_ARROW,
        "home": Keycode.HOME,
        "end": Keycode.END,
        "page_up": Keycode.PAGE_UP,
        "pagedown": Keycode.PAGE_DOWN,
        "page_down": Keycode.PAGE_DOWN,
        "insert": Keycode.INSERT,
        "delete": Keycode.DELETE,
        "print_screen": Keycode.PRINT_SCREEN,
    }

    if token in key_map:
        return key_map[token]

    if len(token) == 1 and "a" <= token <= "z":
        return getattr(Keycode, token.upper())
    if token.isdigit():
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
        return digit_map.get(token)
    if token.startswith("f") and token[1:].isdigit():
        try:
            return getattr(Keycode, token.upper())
        except AttributeError:
            return None

    return None


def execute_special_key_sequence(tokens):
    """Execute keyboard or media output for a special action entry."""
    if not tokens:
        return

    if isinstance(tokens, str):
        tokens = [tokens]

    if len(tokens) == 1:
        media_map = {
            "media_volume_up": ConsumerControlCode.VOLUME_INCREMENT,
            "media_volume_down": ConsumerControlCode.VOLUME_DECREMENT,
            "media_mute": ConsumerControlCode.MUTE,
            "media_play_pause": ConsumerControlCode.PLAY_PAUSE,
        }
        media_code = media_map.get(normalize_token(tokens[0]))
        if media_code is not None:
            cc.send(media_code)
            return

    keycodes = []
    for token in tokens:
        keycode = token_to_keycode(token)
        if keycode is None:
            print(f"Unsupported special token: {token}")
            return
        keycodes.append(keycode)

    kbd = Keyboard(usb_hid.devices)
    kbd.press(*keycodes)
    time.sleep(0.05)
    kbd.release_all()


def run_special_action(action_id, actions):
    """Run a mapped special action and return internal action string if present."""
    entry = actions.get(action_id, SPECIAL_DEFAULTS.get(action_id, {}))
    if "key" in entry:
        execute_special_key_sequence(entry.get("key", []))
        return None
    return entry.get("action", "none")


special_actions = load_special_actions()

is_showing_image = False
image_display_start = 0

def draw_bubbles(selected_index):
    splash = displayio.Group()
    bg_bitmap = displayio.Bitmap(display.width, display.height, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000000
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
    splash.append(bg_sprite)
    display.root_group = splash

    profile_name = get_profile_name(selected_index)
    profile_label = label.Label(terminalio.FONT, text=profile_name, color=0xFFFFFF)
    profile_label.x = (display.width - profile_label.bounding_box[2]) // 2
    profile_label.y = 10
    splash.append(profile_label)

    bubble_width = 14
    bubble_gap = 8
    total_bubbles = 6
    total_width = (bubble_width * 3) + (bubble_gap * 2)
    start_x = (display.width - total_width) // 2
    start_y = profile_label.y + profile_label.bounding_box[3] + 5

    for i in range(total_bubbles):
        x = start_x + (i % 3) * (bubble_width + bubble_gap)
        y = start_y + (i // 3) * (bubble_width + bubble_gap)
        is_selected = (i == selected_index)

        if is_selected:
            bubble_bitmap = displayio.Bitmap(bubble_width, bubble_width, 2)
            bubble_palette = displayio.Palette(2)
            bubble_palette[0] = 0xFFFFFF
            bubble_palette[1] = 0x000000
            for px in range(bubble_width):
                for py in range(bubble_width):
                    if px in (0, bubble_width - 1) or py in (0, bubble_width - 1):
                        bubble_bitmap[px, py] = 0
                    else:
                        bubble_bitmap[px, py] = 1
            bubble_sprite = displayio.TileGrid(bubble_bitmap, pixel_shader=bubble_palette, x=x, y=y)
            splash.append(bubble_sprite)
            number_label = label.Label(terminalio.FONT, text=str(i + 1), color=0xFFFFFF)
        else:
            bubble_bitmap = displayio.Bitmap(bubble_width, bubble_width, 1)
            bubble_palette = displayio.Palette(1)
            bubble_palette[0] = 0xFFFFFF
            bubble_sprite = displayio.TileGrid(bubble_bitmap, pixel_shader=bubble_palette, x=x, y=y)
            splash.append(bubble_sprite)
            number_label = label.Label(terminalio.FONT, text=str(i + 1), color=0x000000)

        number_label.x = x + (bubble_width - number_label.bounding_box[2]) // 2
        number_label.y = y + (bubble_width - number_label.bounding_box[3]) // 2 + 6
        splash.append(number_label)

def get_profile_name(profile_index):
    profile_names = ["Default", "VSCode", "OBS", "Softwares", "Windows", "Photoshop"]
    return profile_names[profile_index] if 0 <= profile_index < len(profile_names) else "Profile"

def load_image(profile_index):
    image_file = image_files[profile_index]
    try:
        bitmap = displayio.OnDiskBitmap(open(image_file, "rb"))
        return bitmap
    except Exception as e:
        print(f"Error loading image {image_file}: {e}")
        return None

draw_bubbles(selected_index)

while True:
    # Volume control on encoder1
    position = encoder1.position
    if last_position_encoder1 is None:
        last_position_encoder1 = position
    if position > last_position_encoder1:
        run_special_action("volume_encoder_right", special_actions)
    elif position < last_position_encoder1:
        run_special_action("volume_encoder_left", special_actions)
    last_position_encoder1 = position

    # Read software-based encoder2
    softEncoder2.update()
    pos2 = softEncoder2.position
    if last_softPos2 is None:
        last_softPos2 = pos2
    delta2 = pos2 - last_softPos2
    if abs(delta2) > 0:  # apply a threshold check if needed
        if delta2 > 0:
            internal_action = run_special_action("display_encoder_right", special_actions)
            if internal_action == "profile_next":
                selected_index = (selected_index + 1) % len(image_files)
                draw_bubbles(selected_index)
            elif internal_action == "profile_prev":
                selected_index = (selected_index - 1) % len(image_files)
                draw_bubbles(selected_index)
        else:
            internal_action = run_special_action("display_encoder_left", special_actions)
            if internal_action == "profile_next":
                selected_index = (selected_index + 1) % len(image_files)
                draw_bubbles(selected_index)
            elif internal_action == "profile_prev":
                selected_index = (selected_index - 1) % len(image_files)
                draw_bubbles(selected_index)
        last_softPos2 = pos2

    #mic mute switch logic
    if not mute_mic.value and debounce_check(last_mic_action_time):
        run_special_action("mic_key", special_actions)
        last_mic_action_time = time.monotonic()
          
    current_volume_button_state = encoder1_button.value
    
    if not current_volume_button_state and last_volume_button_state:
        volume_hold_start = time.monotonic()
        is_holding_volume_button = True
    if current_volume_button_state and not last_volume_button_state:
        if is_holding_volume_button and (time.monotonic() - volume_hold_start) < 1:
            run_special_action("volume_encoder_click", special_actions)
        volume_hold_start = None
        is_holding_volume_button = False
    if is_holding_volume_button and volume_hold_start and (time.monotonic() - volume_hold_start) >= 1:
        run_special_action("volume_encoder_hold", special_actions)
        volume_hold_start = None
        is_holding_volume_button = False
    last_volume_button_state = current_volume_button_state
    
    # encoder2 button logic (click/hold)
    current_display_button_state = encoder2_button.value
    if not current_display_button_state and last_display_button_state and debounce_check(last_encoder2_action_time, 0.2):
        display_hold_start = time.monotonic()
        is_holding_display_button = True
    if current_display_button_state and not last_display_button_state:
        if is_holding_display_button and display_hold_start and (time.monotonic() - display_hold_start) < 1:
            internal_action = run_special_action("display_encoder_click", special_actions)
            if internal_action == "profile_next":
                selected_index = (selected_index + 1) % len(image_files)
            elif internal_action == "profile_prev":
                selected_index = (selected_index - 1) % len(image_files)

            if internal_action in ("profile_next", "profile_prev"):
                bitmap = load_image(selected_index)
                if bitmap:
                    splash = displayio.Group()
                    image_sprite = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
                    image_sprite.x = (display.width - bitmap.width) // 2
                    image_sprite.y = (display.height - bitmap.height) // 2
                    splash.append(image_sprite)
                    display.root_group = splash
                    is_showing_image = True
                    image_display_start = time.monotonic()
            last_encoder2_action_time = time.monotonic()
        display_hold_start = None
        is_holding_display_button = False

    if is_holding_display_button and display_hold_start and (time.monotonic() - display_hold_start) >= 1:
        internal_action = run_special_action("display_encoder_hold", special_actions)
        if internal_action == "profile_next":
            selected_index = (selected_index + 1) % len(image_files)
            draw_bubbles(selected_index)
        elif internal_action == "profile_prev":
            selected_index = (selected_index - 1) % len(image_files)
            draw_bubbles(selected_index)
        display_hold_start = None
        is_holding_display_button = False
        last_encoder2_action_time = time.monotonic()

    last_display_button_state = current_display_button_state
        
    #profile
    for row_index, row_pin in enumerate(rows):
        row_pin.value = True
        for col_index, col_pin in enumerate(cols):
            if col_pin.value and (time.monotonic() - last_key_press_time > debounce_delay):
                key_number = key_mapping[(row_index, col_index)]
                execute_action(key_number, selected_index)
                last_key_press_time = time.monotonic()
        row_pin.value = False

    # Add this code at the end of the while loop to check if it's time to switch back to bubbles
    if is_showing_image and (time.monotonic() - image_display_start) >= 1.0:
        draw_bubbles(selected_index)
        is_showing_image = False