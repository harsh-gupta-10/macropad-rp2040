import time
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

encoder1 = IncrementalEncoder(board.GP18, board.GP19)
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

softEncoder2 = SoftwareEncoder(board.GP14, board.GP15)
last_softPos2 = None

encoder1_button = digitalio.DigitalInOut(board.GP17)
encoder1_button.direction = Direction.INPUT
encoder1_button.pull = Pull.UP

encoder2_button = digitalio.DigitalInOut(board.GP20)
encoder2_button.direction = digitalio.Direction.INPUT
encoder2_button.pull = digitalio.Pull.UP

hold_start = None
is_holding_button = False
last_button_state = True

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
last_action_time = 0

mute_mic = setup_button(board.GP0)

rows = [digitalio.DigitalInOut(pin) for pin in [board.GP1, board.GP2, board.GP3]]
cols = [digitalio.DigitalInOut(pin) for pin in [board.GP4, board.GP13, board.GP6]]

for row in rows:
    row.direction = digitalio.Direction.OUTPUT
    row.value = False
for col in cols:
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.DOWN

key_mapping = {
    (0, 0): 7, (0, 1): 4, (0, 2): 1,
    (1, 0): 8, (1, 1): 5, (1, 2): 2,
    (2, 0): 9, (2, 1): 6, (2, 2): 3,
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

last_button_state = True
last_action_time = 0
is_muted = False

draw_bubbles(selected_index)

while True:
    # Volume control on encoder1
    position = encoder1.position
    if last_position_encoder1 is None:
        last_position_encoder1 = position
    if position > last_position_encoder1:
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
    elif position < last_position_encoder1:
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
    last_position_encoder1 = position

    # Read software-based encoder2
    softEncoder2.update()
    pos2 = softEncoder2.position
    if last_softPos2 is None:
        last_softPos2 = pos2
    delta2 = pos2 - last_softPos2
    if abs(delta2) > 0:  # apply a threshold check if needed
        if delta2 > 0:
            selected_index = (selected_index + 1) % len(image_files)
            draw_bubbles(selected_index)
        else:
            selected_index = (selected_index - 1) % len(image_files)
            draw_bubbles(selected_index)
        last_softPos2 = pos2

    #mic mute switch logic
    if not mute_mic.value and debounce_check(last_action_time):
        kbd = Keyboard(usb_hid.devices)
        kbd.press(Keycode.F13)
        kbd.release_all()
        last_action_time = time.monotonic()
          
    current_button_state = encoder1_button.value
    
    if not current_button_state and last_button_state:
        hold_start = time.monotonic()
        is_holding_button = True
    if current_button_state and not last_button_state:
        if is_holding_button and (time.monotonic() - hold_start) < 2:
            cc.send(ConsumerControlCode.PLAY_PAUSE)
        hold_start = None
        is_holding_button = False
    if is_holding_button and hold_start and (time.monotonic() - hold_start) >= 1:
        cc.send(ConsumerControlCode.MUTE)
        hold_start = None
        is_holding_button = False
    last_button_state = current_button_state
    
    #encoder2 button logic to switch betwwen profiles
    if not encoder2_button.value and debounce_check(last_action_time):
        selected_index = (selected_index + 1) % 6
        # Load and display the image instead of bubbles
        bitmap = load_image(selected_index)
        if bitmap:
            splash = displayio.Group()
            image_sprite = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
            # Center the image on the display
            image_sprite.x = (display.width - bitmap.width) // 2
            image_sprite.y = (display.height - bitmap.height) // 2
            splash.append(image_sprite)
            display.root_group = splash
            is_showing_image = True
            image_display_start = time.monotonic()
        last_action_time = time.monotonic()
        
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
