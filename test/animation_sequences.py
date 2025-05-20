from flux_garage_roboeyes import RoboEyes
import board
import busio
import displayio
import adafruit_displayio_sh1106
import time

# Initialize I2C and display
i2c = busio.I2C(board.GP9, board.GP8)
display = adafruit_displayio_sh1106.SH1106(displayio.I2CDisplay(i2c, device_address=0x3C), width=128, height=64)

# Create an instance of the RoboEyes class
robo_eyes = RoboEyes(display)

# Function to run various animation sequences
def run_animation_sequences():
    # Set initial parameters
    robo_eyes.set_width(36, 36)
    robo_eyes.set_height(36, 36)
    robo_eyes.set_borderradius(8, 8)
    robo_eyes.set_spacebetween(10)
    
    # Start with default mood
    robo_eyes.set_mood(robo_eyes.DEFAULT)
    
    # Run a sequence of animations
    while True:
        # Blink animation
        robo_eyes.blink()
        time.sleep(1)

        # Set mood to happy and animate
        robo_eyes.set_mood(robo_eyes.HAPPY)
        for _ in range(5):
            robo_eyes.anim_laugh()
            time.sleep(0.5)

        # Set mood to tired and animate
        robo_eyes.set_mood(robo_eyes.TIRED)
        for _ in range(5):
            robo_eyes.blink()
            time.sleep(0.5)

        # Set mood to angry and animate
        robo_eyes.set_mood(robo_eyes.ANGRY)
        for _ in range(5):
            robo_eyes.anim_confused()
            time.sleep(0.5)

        # Reset to default mood
        robo_eyes.set_mood(robo_eyes.DEFAULT)
        time.sleep(2)

# Run the animation sequences
run_animation_sequences()