"""
FluxGarage RoboEyes for CircuitPython OLED Displays
Adapted from the Arduino C++ version to work with CircuitPython displayio
Uses similar drawing concepts as Adafruit GFX library like fillRoundRect and fillTriangle

Copyright (C) 2024 Dennis Hoelscher (original C++ version)
CircuitPython port maintains compatibility with original API
"""

import displayio
import time
import random
import math
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle

# Constants
# For mood type switch
DEFAULT = 0
TIRED = 1
ANGRY = 2
HAPPY = 3

# For turning things on or off
ON = True
OFF = False

# For switch "predefined positions"
N = 1  # north, top center
NE = 2  # north-east, top right
E = 3  # east, middle right
SE = 4  # south-east, bottom right
S = 5  # south, bottom center
SW = 6  # south-west, bottom left
W = 7  # west, middle left
NW = 8  # north-west, top left
# for middle center set "DEFAULT"

class RoboEyes(displayio.Group):
    def __init__(self, display):
        super().__init__()
        self.display = display
        
        # Screen properties
        self.screen_width = 128
        self.screen_height = 64
        self.frame_interval = 20  # default for 50 FPS
        self.fps_timer = time.monotonic()
        
        # For controlling mood types and expressions
        self.tired = False
        self.angry = False
        self.happy = False
        self.curious = False
        self.cyclops = False
        self.eye_l_open = False
        self.eye_r_open = False
        
        # Space between eyes
        self.space_between_default = 10
        self.space_between_current = self.space_between_default
        self.space_between_next = 10
        
        # EYE LEFT - size and border radius
        self.eye_l_width_default = 36
        self.eye_l_height_default = 36
        self.eye_l_width_current = self.eye_l_width_default
        self.eye_l_height_current = 1  # start with closed eye
        self.eye_l_width_next = self.eye_l_width_default
        self.eye_l_height_next = self.eye_l_height_default
        self.eye_l_height_offset = 0
        
        # Border Radius
        self.eye_l_border_radius_default = 8
        self.eye_l_border_radius_current = self.eye_l_border_radius_default
        self.eye_l_border_radius_next = self.eye_l_border_radius_default
        
        # EYE RIGHT - size and border radius
        self.eye_r_width_default = self.eye_l_width_default
        self.eye_r_height_default = self.eye_l_height_default
        self.eye_r_width_current = self.eye_r_width_default
        self.eye_r_height_current = 1  # start with closed eye
        self.eye_r_width_next = self.eye_r_width_default
        self.eye_r_height_next = self.eye_r_height_default
        self.eye_r_height_offset = 0
        
        # Border Radius
        self.eye_r_border_radius_default = 8
        self.eye_r_border_radius_current = self.eye_r_border_radius_default
        self.eye_r_border_radius_next = self.eye_r_border_radius_default
        
        # EYE LEFT - Coordinates
        self.eye_l_x_default = ((self.screen_width) - (self.eye_l_width_default + self.space_between_default + self.eye_r_width_default)) // 2
        self.eye_l_y_default = ((self.screen_height - self.eye_l_height_default) // 2)
        self.eye_l_x = self.eye_l_x_default
        self.eye_l_y = self.eye_l_y_default
        self.eye_l_x_next = self.eye_l_x
        self.eye_l_y_next = self.eye_l_y
        
        # EYE RIGHT - Coordinates
        self.eye_r_x_default = self.eye_l_x + self.eye_l_width_current + self.space_between_default
        self.eye_r_y_default = self.eye_l_y
        self.eye_r_x = self.eye_r_x_default
        self.eye_r_y = self.eye_r_y_default
        self.eye_r_x_next = self.eye_r_x
        self.eye_r_y_next = self.eye_r_y
        
        # BOTH EYES
        # Eyelid top size
        self.eyelids_height_max = self.eye_l_height_default // 2
        self.eyelids_tired_height = 0
        self.eyelids_tired_height_next = self.eyelids_tired_height
        self.eyelids_angry_height = 0
        self.eyelids_angry_height_next = self.eyelids_angry_height
        
        # Bottom happy eyelids offset
        self.eyelids_happy_bottom_offset_max = (self.eye_l_height_default // 2) + 3
        self.eyelids_happy_bottom_offset = 0
        self.eyelids_happy_bottom_offset_next = 0
        
        # Animation - horizontal flicker/shiver
        self.h_flicker = False
        self.h_flicker_alternate = False
        self.h_flicker_amplitude = 2
        
        # Animation - vertical flicker/shiver
        self.v_flicker = False
        self.v_flicker_alternate = False
        self.v_flicker_amplitude = 10
        
        # Animation - auto blinking
        self.autoblinker = False
        self.blink_interval = 1
        self.blink_interval_variation = 4
        self.blink_timer = 0
        
        # Animation - idle mode
        self.idle = False
        self.idle_interval = 1
        self.idle_interval_variation = 3
        self.idle_animation_timer = 0
        
        # Animation - eyes confused
        self.confused = False
        self.confused_animation_timer = 0
        self.confused_animation_duration = 0.5
        self.confused_toggle = True
        
        # Animation - eyes laughing
        self.laugh = False
        self.laugh_animation_timer = 0
        self.laugh_animation_duration = 0.5
        self.laugh_toggle = True
        
        # Drawing colors
        self.BGCOLOR = 0x000000  # Black
        self.MAINCOLOR = 0xFFFFFF  # White
        
        # Create a group for the eyes
        self.eyes_group = displayio.Group()
        self.append(self.eyes_group)

    def begin(self, width, height, frame_rate):
        """Initialize the RoboEyes with screen dimensions and frame rate"""
        self.screen_width = width
        self.screen_height = height
        self.eye_l_height_current = 1  # start with closed eyes
        self.eye_r_height_current = 1  # start with closed eyes
        self.set_framerate(frame_rate)
        
    def set_framerate(self, fps):
        """Set the animation frame rate"""
        self.frame_interval = 1.0 / fps
        
    def set_width(self, left_eye, right_eye):
        """Set the width of both eyes"""
        self.eye_l_width_next = left_eye
        self.eye_r_width_next = right_eye
        self.eye_l_width_default = left_eye
        self.eye_r_width_default = right_eye
        
    def set_height(self, left_eye, right_eye):
        """Set the height of both eyes"""
        self.eye_l_height_next = left_eye
        self.eye_r_height_next = right_eye
        self.eye_l_height_default = left_eye
        self.eye_r_height_default = right_eye
        
    def set_border_radius(self, left_eye, right_eye):
        """Set the border radius of both eyes"""
        self.eye_l_border_radius_next = left_eye
        self.eye_r_border_radius_next = right_eye
        self.eye_l_border_radius_default = left_eye
        self.eye_r_border_radius_default = right_eye
        
    def set_space_between(self, space):
        """Set the space between eyes"""
        self.space_between_next = space
        self.space_between_default = space
        
    def set_mood(self, mood):
        """Set the mood expression of the eyes"""
        if mood == TIRED:
            self.tired = True
            self.angry = False
            self.happy = False
        elif mood == ANGRY:
            self.tired = False
            self.angry = True
            self.happy = False
        elif mood == HAPPY:
            self.tired = False
            self.angry = False
            self.happy = True
        else:  # DEFAULT
            self.tired = False
            self.angry = False
            self.happy = False
    
    def set_position(self, position):
        """Set predefined eye position"""
        if position == N:
            # North, top center
            self.eye_l_x_next = self.get_screen_constraint_x() // 2
            self.eye_l_y_next = 0
        elif position == NE:
            # North-east, top right
            self.eye_l_x_next = self.get_screen_constraint_x()
            self.eye_l_y_next = 0
        elif position == E:
            # East, middle right
            self.eye_l_x_next = self.get_screen_constraint_x()
            self.eye_l_y_next = self.get_screen_constraint_y() // 2
        elif position == SE:
            # South-east, bottom right
            self.eye_l_x_next = self.get_screen_constraint_x()
            self.eye_l_y_next = self.get_screen_constraint_y()
        elif position == S:
            # South, bottom center
            self.eye_l_x_next = self.get_screen_constraint_x() // 2
            self.eye_l_y_next = self.get_screen_constraint_y()
        elif position == SW:
            # South-west, bottom left
            self.eye_l_x_next = 0
            self.eye_l_y_next = self.get_screen_constraint_y()
        elif position == W:
            # West, middle left
            self.eye_l_x_next = 0
            self.eye_l_y_next = self.get_screen_constraint_y() // 2
        elif position == NW:
            # North-west, top left
            self.eye_l_x_next = 0
            self.eye_l_y_next = 0
        else:
            # Middle center (DEFAULT)
            self.eye_l_x_next = self.get_screen_constraint_x() // 2
            self.eye_l_y_next = self.get_screen_constraint_y() // 2
    
    def set_cyclops(self, cyclops_bit):
        """Set cyclops mode (single eye)"""
        self.cyclops = cyclops_bit
        
    def set_curiosity(self, curious_bit):
        """Set curious mode (eyes change size when looking to edges)"""
        self.curious = curious_bit
        
    def set_autoblinker(self, active, interval=None, variation=None):
        """Set auto-blink mode"""
        self.autoblinker = active
        if interval is not None:
            self.blink_interval = interval
        if variation is not None:
            self.blink_interval_variation = variation
        self.blink_timer = time.monotonic()
    
    def set_idle_mode(self, active, interval=None, variation=None):
        """Set idle mode (random eye movements)"""
        self.idle = active
        if interval is not None:
            self.idle_interval = interval
        if variation is not None:
            self.idle_interval_variation = variation
        self.idle_animation_timer = time.monotonic()
    
    def set_h_flicker(self, flicker_bit, amplitude=None):
        """Set horizontal flickering/shivering"""
        self.h_flicker = flicker_bit
        if amplitude is not None:
            self.h_flicker_amplitude = amplitude
            
    def set_v_flicker(self, flicker_bit, amplitude=None):
        """Set vertical flickering/shivering"""
        self.v_flicker = flicker_bit
        if amplitude is not None:
            self.v_flicker_amplitude = amplitude
    
    def get_screen_constraint_x(self):
        """Returns the max x position for left eye"""
        return self.screen_width - self.eye_l_width_current - self.space_between_current - self.eye_r_width_current
        
    def get_screen_constraint_y(self):
        """Returns the max y position for left eye"""
        return self.screen_height - self.eye_l_height_default
    
    def close(self, left=True, right=True):
        """Close one or both eyes"""
        if left:
            self.eye_l_height_next = 1
            self.eye_l_open = False
        if right:
            self.eye_r_height_next = 1
            self.eye_r_open = False
            
    def open(self, left=True, right=True):
        """Open one or both eyes"""
        if left:
            self.eye_l_open = True
        if right:
            self.eye_r_open = True
            
    def blink(self, left=True, right=True):
        """Trigger eye blink animation"""
        self.close(left, right)
        self.open(left, right)
        
    def anim_confused(self):
        """Play confused animation - eyes shaking left and right"""
        self.confused = True
        self.confused_animation_timer = time.monotonic()
        self.confused_toggle = True
        
    def anim_laugh(self):
        """Play laugh animation - eyes shaking up and down"""
        self.laugh = True
        self.laugh_animation_timer = time.monotonic()
        self.laugh_toggle = True
        
    def update(self):
        """Update the eye animations based on frame rate"""
        current_time = time.monotonic()
        
        # Only update if enough time has passed (respect frame rate)
        if current_time - self.fps_timer >= self.frame_interval:
            self.fps_timer = current_time
            self._draw_eyes()
    
    def _draw_eyes(self):
        """Internal method to draw the eyes with all animations and effects"""
        # Clear previous drawings
        while len(self.eyes_group) > 0:
            self.eyes_group.pop()
        
        # PRE-CALCULATIONS - EYE SIZES AND VALUES FOR ANIMATION TWEENINGS
        
        # Vertical size offset for larger eyes when looking left or right (curious gaze)
        if self.curious:
            if self.eye_l_x_next <= 10:
                self.eye_l_height_offset = 8
            elif self.eye_l_x_next >= (self.get_screen_constraint_x() - 10) and self.cyclops:
                self.eye_l_height_offset = 8
            else:
                self.eye_l_height_offset = 0
                
            if self.eye_r_x_next >= self.screen_width - self.eye_r_width_current - 10:
                self.eye_r_height_offset = 8
            else:
                self.eye_r_height_offset = 0
        else:
            self.eye_l_height_offset = 0
            self.eye_r_height_offset = 0
        
        # Left eye height
        self.eye_l_height_current = (self.eye_l_height_current + self.eye_l_height_next + self.eye_l_height_offset) // 2
        temp_l_y = self.eye_l_y
        temp_l_y += ((self.eye_l_height_default - self.eye_l_height_current) // 2)  # vertical centering of eye when closing
        temp_l_y -= self.eye_l_height_offset // 2
        
        # Right eye height
        self.eye_r_height_current = (self.eye_r_height_current + self.eye_r_height_next + self.eye_r_height_offset) // 2
        temp_r_y = self.eye_r_y
        temp_r_y += (self.eye_r_height_default - self.eye_r_height_current) // 2  # vertical centering of eye when closing
        temp_r_y -= self.eye_r_height_offset // 2
        
        # Open eyes again after closing them
        if self.eye_l_open:
            if self.eye_l_height_current <= 1 + self.eye_l_height_offset:
                self.eye_l_height_next = self.eye_l_height_default
                
        if self.eye_r_open:
            if self.eye_r_height_current <= 1 + self.eye_r_height_offset:
                self.eye_r_height_next = self.eye_r_height_default
        
        # Left eye width
        self.eye_l_width_current = (self.eye_l_width_current + self.eye_l_width_next) // 2
        
        # Right eye width
        self.eye_r_width_current = (self.eye_r_width_current + self.eye_r_width_next) // 2
        
        # Space between eyes
        self.space_between_current = (self.space_between_current + self.space_between_next) // 2
        
        # Left eye coordinates
        self.eye_l_x = (self.eye_l_x + self.eye_l_x_next) // 2
        self.eye_l_y = (self.eye_l_y + self.eye_l_y_next) // 2
        
        # Right eye coordinates
        self.eye_r_x_next = self.eye_l_x_next + self.eye_l_width_current + self.space_between_current
        self.eye_r_y_next = self.eye_l_y_next
        self.eye_r_x = (self.eye_r_x + self.eye_r_x_next) // 2
        self.eye_r_y = (self.eye_r_y + self.eye_r_y_next) // 2
        
        # Left eye border radius
        self.eye_l_border_radius_current = (self.eye_l_border_radius_current + self.eye_l_border_radius_next) // 2
        
        # Right eye border radius
        self.eye_r_border_radius_current = (self.eye_r_border_radius_current + self.eye_r_border_radius_next) // 2
        
        # APPLYING MACRO ANIMATIONS
        
        # Auto blinker
        if self.autoblinker:
            current_time = time.monotonic()
            if current_time >= self.blink_timer:
                self.blink()
                variation = random.randint(0, self.blink_interval_variation)
                self.blink_timer = current_time + self.blink_interval + variation
        
        # Laughing animation
        if self.laugh:
            current_time = time.monotonic()
            if self.laugh_toggle:
                self.set_v_flicker(True, 5)
                self.laugh_toggle = False
            elif current_time >= self.laugh_animation_timer + self.laugh_animation_duration:
                self.set_v_flicker(False)
                self.laugh_toggle = True
                self.laugh = False
        
        # Confused animation
        if self.confused:
            current_time = time.monotonic()
            if self.confused_toggle:
                self.set_h_flicker(True, 20)
                self.confused_toggle = False
            elif current_time >= self.confused_animation_timer + self.confused_animation_duration:
                self.set_h_flicker(False)
                self.confused_toggle = True
                self.confused = False
        
        # Idle mode - eyes moving to random positions
        if self.idle:
            current_time = time.monotonic()
            if current_time >= self.idle_animation_timer:
                self.eye_l_x_next = random.randint(0, self.get_screen_constraint_x())
                self.eye_l_y_next = random.randint(0, self.get_screen_constraint_y())
                variation = random.randint(0, self.idle_interval_variation)
                self.idle_animation_timer = current_time + self.idle_interval + variation
        
        # Horizontal flickering/shivering
        temp_l_x = self.eye_l_x
        temp_r_x = self.eye_r_x
        if self.h_flicker:
            if self.h_flicker_alternate:
                temp_l_x += self.h_flicker_amplitude
                temp_r_x += self.h_flicker_amplitude
            else:
                temp_l_x -= self.h_flicker_amplitude
                temp_r_x -= self.h_flicker_amplitude
            self.h_flicker_alternate = not self.h_flicker_alternate
        
        # Vertical flickering/shivering
        if self.v_flicker:
            if self.v_flicker_alternate:
                temp_l_y += self.v_flicker_amplitude
                temp_r_y += self.v_flicker_amplitude
            else:
                temp_l_y -= self.v_flicker_amplitude
                temp_r_y -= self.v_flicker_amplitude
            self.v_flicker_alternate = not self.v_flicker_alternate
        
        # Cyclops mode
        if self.cyclops:
            self.eye_r_width_current = 0
            self.eye_r_height_current = 0
            self.space_between_current = 0
        
        # ACTUAL DRAWINGS - Using adafruit_display_shapes to mimic Adafruit GFX
        
        # Draw basic eye rectangles
        if self.eye_l_width_current > 0 and self.eye_l_height_current > 0:
            left_eye = RoundRect(
                temp_l_x, temp_l_y, 
                self.eye_l_width_current, 
                self.eye_l_height_current, 
                self.eye_l_border_radius_current,
                fill=self.MAINCOLOR
            )
            self.eyes_group.append(left_eye)
        
        # Right eye (only if not in cyclops mode)
        if not self.cyclops and self.eye_r_width_current > 0 and self.eye_r_height_current > 0:
            right_eye = RoundRect(
                temp_r_x, temp_r_y, 
                self.eye_r_width_current, 
                self.eye_r_height_current, 
                self.eye_r_border_radius_current,
                fill=self.MAINCOLOR
            )
            self.eyes_group.append(right_eye)
        
        # Prepare mood type transitions
        if self.tired:
            self.eyelids_tired_height_next = self.eye_l_height_current // 2
            self.eyelids_angry_height_next = 0
        else:
            self.eyelids_tired_height_next = 0
            
        if self.angry:
            self.eyelids_angry_height_next = self.eye_l_height_current // 2
            self.eyelids_tired_height_next = 0
        else:
            self.eyelids_angry_height_next = 0
            
        if self.happy:
            self.eyelids_happy_bottom_offset_next = self.eye_l_height_current // 2
        else:
            self.eyelids_happy_bottom_offset_next = 0
        
        # Draw tired top eyelids
        self.eyelids_tired_height = (self.eyelids_tired_height + self.eyelids_tired_height_next) // 2
        if self.eyelids_tired_height > 0:
            if not self.cyclops:
                # Left eye
                left_tired = Triangle(
                    temp_l_x, temp_l_y - 1,
                    temp_l_x + self.eye_l_width_current, temp_l_y - 1,
                    temp_l_x, temp_l_y + self.eyelids_tired_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(left_tired)
                
                # Right eye
                right_tired = Triangle(
                    temp_r_x, temp_r_y - 1,
                    temp_r_x + self.eye_r_width_current, temp_r_y - 1,
                    temp_r_x + self.eye_r_width_current, temp_r_y + self.eyelids_tired_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(right_tired)
            else:
                # Cyclops tired eyelids
                left_half = Triangle(
                    temp_l_x, temp_l_y - 1,
                    temp_l_x + (self.eye_l_width_current // 2), temp_l_y - 1,
                    temp_l_x, temp_l_y + self.eyelids_tired_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(left_half)
                
                right_half = Triangle(
                    temp_l_x + (self.eye_l_width_current // 2), temp_l_y - 1,
                    temp_l_x + self.eye_l_width_current, temp_l_y - 1,
                    temp_l_x + self.eye_l_width_current, temp_l_y + self.eyelids_tired_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(right_half)
        
        # Draw angry top eyelids
        self.eyelids_angry_height = (self.eyelids_angry_height + self.eyelids_angry_height_next) // 2
        if self.eyelids_angry_height > 0:
            if not self.cyclops:
                # Left eye
                left_angry = Triangle(
                    temp_l_x, temp_l_y - 1,
                    temp_l_x + self.eye_l_width_current, temp_l_y - 1,
                    temp_l_x + self.eye_l_width_current, temp_l_y + self.eyelids_angry_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(left_angry)
                
                # Right eye
                right_angry = Triangle(
                    temp_r_x, temp_r_y - 1,
                    temp_r_x + self.eye_r_width_current, temp_r_y - 1,
                    temp_r_x, temp_r_y + self.eyelids_angry_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(right_angry)
            else:
                # Cyclops angry eyelids
                left_half = Triangle(
                    temp_l_x, temp_l_y - 1,
                    temp_l_x + (self.eye_l_width_current // 2), temp_l_y - 1,
                    temp_l_x + (self.eye_l_width_current // 2), temp_l_y + self.eyelids_angry_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(left_half)
                
                right_half = Triangle(
                    temp_l_x + (self.eye_l_width_current // 2), temp_l_y - 1,
                    temp_l_x + self.eye_l_width_current, temp_l_y - 1,
                    temp_l_x + (self.eye_l_width_current // 2), temp_l_y + self.eyelids_angry_height - 1,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(right_half)
        
        # Draw happy bottom eyelids
        self.eyelids_happy_bottom_offset = (self.eyelids_happy_bottom_offset + self.eyelids_happy_bottom_offset_next) // 2
        if self.eyelids_happy_bottom_offset > 0:
            # Left eye
            left_happy = RoundRect(
                temp_l_x - 1, 
                (temp_l_y + self.eye_l_height_current) - self.eyelids_happy_bottom_offset + 1, 
                self.eye_l_width_current + 2, 
                self.eye_l_height_default, 
                self.eye_l_border_radius_current,
                fill=self.BGCOLOR
            )
            self.eyes_group.append(left_happy)
            
            # Right eye (only if not in cyclops mode)
            if not self.cyclops:
                right_happy = RoundRect(
                    temp_r_x - 1, 
                    (temp_r_y + self.eye_r_height_current) - self.eyelids_happy_bottom_offset + 1, 
                    self.eye_r_width_current + 2, 
                    self.eye_r_height_default, 
                    self.eye_r_border_radius_current,
                    fill=self.BGCOLOR
                )
                self.eyes_group.append(right_happy)
