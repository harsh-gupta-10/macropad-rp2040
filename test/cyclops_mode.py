from adafruit_displayio import Display
from adafruit_displayio_sh1106 import SH1106
import displayio
import board
import busio
from flux_garage_roboeyes import RoboEyes

# Initialize I2C for the display
i2c = busio.I2C(board.SCL, board.SDA)

# Create the display context
display = Display(i2c, width=128, height=64)

# Create an instance of the RoboEyes class
robo_eyes = RoboEyes(display)

# Set cyclops mode
robo_eyes.set_cyclops(True)

# Main loop
while True:
    # Update the eyes
    robo_eyes.update()