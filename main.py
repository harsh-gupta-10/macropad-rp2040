import board

from kmk.boards.OGDECK import KMKKeyboard
from kmk.keys import KC
from kmk.modules.encoder import EncoderHandler
from kmk.handlers.sequences import send_string
from kmk.handlers.sequences import simple_key_sequence
from kmk.modules.layers import Layers
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.mouse_keys import MouseKeys
from kmk.extensions.RGB import RGB

keyboard = KMKKeyboard()
keyboard.debug_enabled = True

rgb = RGB(pixel_pin=board.GP6, num_pixels=17, val_limit=64)

class _Layers(Layers):
    last_top_layer = 0
    hues = (4, 20, 69)

    def after_hid_send(self, keyboard):
        if keyboard.active_layers[0] != self.last_top_layer:
            self.last_top_layer = keyboard.active_layers[0]
            rgb.set_hsv_fill(self.hues[self.last_top_layer], 255, 255)


encoder_handler = EncoderHandler()
keyboard.modules.append(_Layers())
keyboard.modules.append(encoder_handler)
keyboard.modules.append(MouseKeys())
keyboard.extensions.append(MediaKeys())
keyboard.extensions.append(rgb)

encoder_handler.pins = (
    (board.GP2, board.GP3, None),  # encoder #2
    (board.GP0, board.GP1, None),  # encoder #1
)

KNOB00_ANTI_CLOCKWISE = KC.NO
KNOB00_BUTTON = KC.NO
KNOB00_CLOCKWISE = KC.NO
KNOB01_ANTI_CLOCKWISE = KC.NO
KNOB01_BUTTON = KC.NO
KNOB01_CLOCKWISE = KC.NO
KEY000 = KC.NO
KEY001 = KC.NO
KEY002 = KC.NO
KEY003 = KC.NO
KEY004 = KC.NO
KEY010 = KC.NO
KEY011 = KC.NO
KEY012 = KC.NO
KEY013 = KC.NO
KEY014 = KC.NO
KEY020 = KC.NO
KEY021 = KC.NO
KEY022 = KC.NO
KEY023 = KC.NO
KEY024 = KC.NO
KEY030 = KC.NO
KEY031 = KC.NO
KEY032 = KC.NO
KEY033 = KC.NO
KEY034 = KC.NO
KNOB10_ANTI_CLOCKWISE = KC.NO
KNOB10_BUTTON = KC.NO
KNOB10_CLOCKWISE = KC.NO
KNOB11_ANTI_CLOCKWISE = KC.NO
KNOB11_BUTTON = KC.NO
KNOB11_CLOCKWISE = KC.NO
KEY100 = KC.NO
KEY101 = KC.NO
KEY102 = KC.NO
KEY103 = KC.NO
KEY104 = KC.NO
KEY110 = KC.NO
KEY111 = KC.NO
KEY112 = KC.NO
KEY113 = KC.NO
KEY114 = KC.NO
KEY120 = KC.NO
KEY121 = KC.NO
KEY122 = KC.NO
KEY123 = KC.NO
KEY124 = KC.NO
KEY130 = KC.NO
KEY131 = KC.NO
KEY132 = KC.NO
KEY133 = KC.NO
KEY134 = KC.NO
KNOB20_ANTI_CLOCKWISE = KC.NO
KNOB20_BUTTON = KC.NO
KNOB20_CLOCKWISE = KC.NO
KNOB21_ANTI_CLOCKWISE = KC.RSFT(KC.F13)
KNOB21_BUTTON = KC.NO
KNOB21_CLOCKWISE = KC.NO
KEY200 = KC.NO
KEY201 = KC.NO
KEY202 = KC.NO
KEY203 = KC.NO
KEY204 = KC.NO
KEY210 = KC.NO
KEY211 = KC.NO
KEY212 = KC.NO
KEY213 = KC.NO
KEY214 = KC.NO
KEY220 = KC.NO
KEY221 = KC.NO
KEY222 = KC.NO
KEY223 = KC.NO
KEY224 = KC.NO
KEY230 = KC.NO
KEY231 = KC.NO
KEY232 = KC.NO
KEY233 = KC.NO
KEY234 = KC.NO

keyboard.keymap = [
	[
		KEY000, KEY001, KEY002, KEY003, KEY004, 
		KEY010, KEY011, KEY012, KEY013, KEY014, 
		KEY020, KEY021, KEY022, KEY023, KEY024, 
		KEY030, KEY031, KEY032, KEY033, KEY034, 
	],
	[
		KEY100, KEY101, KEY102, KEY103, KEY104, 
		KEY110, KEY111, KEY112, KEY113, KEY114, 
		KEY120, KEY121, KEY122, KEY123, KEY124, 
		KEY130, KEY131, KEY132, KEY133, KEY134, 
	],
	[
		KEY200, KEY201, KEY202, KEY203, KEY204, 
		KEY210, KEY211, KEY212, KEY213, KEY214, 
		KEY220, KEY221, KEY222, KEY223, KEY224, 
		KEY230, KEY231, KEY232, KEY233, KEY234, 
	]
]

encoder_handler.map = [
	((KNOB00_ANTI_CLOCKWISE, KNOB00_CLOCKWISE, KC.NO),(KNOB01_ANTI_CLOCKWISE, KNOB01_CLOCKWISE, KC.NO)),
	((KNOB10_ANTI_CLOCKWISE, KNOB10_CLOCKWISE, KC.NO),(KNOB11_ANTI_CLOCKWISE, KNOB11_CLOCKWISE, KC.NO)),
	((KNOB20_ANTI_CLOCKWISE, KNOB20_CLOCKWISE, KC.NO),(KNOB21_ANTI_CLOCKWISE, KNOB21_CLOCKWISE, KC.NO))
]


if __name__ == '__main__':
    keyboard.go()
