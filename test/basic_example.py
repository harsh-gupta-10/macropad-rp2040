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

# Setup the RoboEyes
robo_eyes.begin(128, 64, 100)  # width, height, max framerate

# Define some automated eyes behavior
robo_eyes.set_autoblinker(True, 3, 2)  # Start auto blink
robo_eyes.set_idle_mode(True, 2, 2)  # Start idle animation

# Main loop
while True:
    robo_eyes.update()  # Update the eyes animations
    display.show(robo_eyes)  # Show the RoboEyes on the display