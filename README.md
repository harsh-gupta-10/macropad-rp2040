# RP2040 MacroPad Firmware

Custom CircuitPython firmware for a DIY macro pad with:

- 3x3 key matrix
- 2 rotary encoders (volume + profile/navigation)
- 1 OLED display (SH1106 over I2C)
- Per-profile actions loaded from JSON
- Editable special actions for encoders and mic key

This repo is set up for an RP2040-based board and runs as a USB HID device (keyboard + media control).

## Features

- 6 profiles, each with 9 key actions
- Profile UI on OLED with quick icon preview when switching
- Volume encoder supports rotate, click, and hold actions
- Second encoder supports profile switching and click/hold actions
- Dedicated mic toggle button
- Action types:
  - Keyboard shortcuts (single key or multi-key combo)
  - Launch software (Windows search + type + enter)
  - Text input macros (single/line-by-line/paragraph)
  - Media controls (volume up/down, mute, play/pause)

## Project Layout

- `code.py`: Main CircuitPython runtime loop (display, matrix scan, encoders, special actions)
- `keyout.py`: Action engine for key combos, software launch, and text typing
- `keysfile.json`: Profile/action definitions for matrix keys
- `special-keyout.json`: Special mappings for encoders and mic button
- `img/`: Bitmap icons used for profile preview
- `lib/`: Required CircuitPython libraries and dependencies
- `main.py`: Alternate KMK-based firmware (not used while `code.py` is present)

## Hardware Pin Map

### OLED (SH1106, I2C, address 0x3C)

- SCL: GP9
- SDA: GP8

### Encoders

- Encoder 1 (volume):
  - A/B: GP14, GP15
  - Button: GP17
- Encoder 2 (software quadrature):
  - A/B: GP18, GP19
  - Button: GP20

### Other Inputs

- Mic toggle button: GP0

### 3x3 Matrix

- Columns (input, pull-down): GP1, GP2, GP3
- Rows (output): GP4, GP13, GP6

Matrix index mapping is defined by `key_mapping` in `code.py`.
If physical button-to-action positions feel wrong, update `key_mapping` first instead of changing `keysfile.json`.

## Controls

- Encoder 1 rotate: volume up/down
- Encoder 1 click: play/pause
- Encoder 1 hold: mute
- Encoder 2 rotate: previous/next profile (configurable)
- Encoder 2 click: switch profile (shows icon briefly)
- Encoder 2 hold: configurable profile action
- Mic button: sends configured mic toggle key (default F13)
- Matrix keys: run current profile actions from `keysfile.json`

## Configuration

### 1) Profile Keys (`keysfile.json`)

Top-level format:

```json
{
  "profiles": {
    "0": {
      "1": {
        "name": "Open Notepad",
        "key": ["windows"],
        "software": "notepad"
      }
    }
  }
}
```

Supported action styles per key:

- Key combo

```json
{
  "name": "Close Tab",
  "key": ["ctrl", "w"]
}
```

- Launch software

```json
{
  "name": "Open VS Code",
  "key": ["windows"],
  "software": "vscode"
}
```

- Text input macro

```json
{
  "name": "Paste Snippet",
  "key": ["text_input"],
  "text_type": "single",
  "text_content": "Hello from macropad"
}
```

`text_type` values:

- `single`
- `line-by-line`
- `paragraph`

### 2) Special Inputs (`special-keyout.json`)

`special_keys` entries control:

- `volume_encoder_left`
- `volume_encoder_right`
- `volume_encoder_click`
- `volume_encoder_hold`
- `display_encoder_left`
- `display_encoder_right`
- `display_encoder_click`
- `display_encoder_hold`
- `mic_key`

Each entry can use either:

- `key`: key/media token list
- `action`: internal action such as `profile_next`, `profile_prev`, or `none`

Example:

```json
{
  "special_keys": {
    "display_encoder_right": {
      "name": "Next Profile",
      "action": "profile_next"
    },
    "volume_encoder_click": {
      "name": "Play/Pause",
      "key": ["media_play_pause"]
    }
  }
}
```

## Setup

1. Flash CircuitPython to your RP2040 board.
2. Copy all project files to CIRCUITPY root.
3. Copy the full `lib/` folder to CIRCUITPY/lib.
4. Keep `code.py` at CIRCUITPY root so it runs on boot.
5. Edit `keysfile.json` and `special-keyout.json` for your workflow.
6. Save files and let the board auto-reload.

## Notes

- This project is currently optimized for Windows-focused shortcuts.
- `main.py` contains a separate KMK firmware path; it is not active while `code.py` exists.
- If a token is unsupported, the firmware prints an error over serial.

## Troubleshooting

- No key output:
  - Confirm USB HID is enabled and board is detected by host OS.
  - Verify key token spelling in JSON.
- Wrong button/action mapping:
  - Adjust `key_mapping` in `code.py`.
- Display not showing:
  - Verify I2C wiring (GP9/GP8) and OLED address (0x3C).
- Special actions not changing:
  - Validate `special-keyout.json` syntax and `special_keys` object shape.