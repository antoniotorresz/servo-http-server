# Import libraries
import RPi.GPIO as GPIO
import time

# Set GPIO pin mode
GPIO.setmode(GPIO.BOARD)

# Set pin 11 as output and define servo1 as PWM pin
GPIO.setup(11, GPIO.OUT)
servo1 = GPIO.PWM(11, 50) # pin 11 for servo1, pulse 50Hz

# Start PWM with a value of 0
servo1.start(0)

"""
This file contains the code for controlling a servo motor on a Raspberry Pi.
Dutty cycle ref: https://en.wikipedia.org/wiki/Duty_cycle
"""

import time

def move_servo():
    """
    Moves the servo motor back and forth continuously.
    """
    try:
        while True:
            servo1.ChangeDutyCycle(6.00)
            time.sleep(0.5)
            servo1.ChangeDutyCycle(2.00)
            time.sleep(210)
    except:
        pass

def stop_servo():
    """
    Stops the servo motor by setting the duty cycle to 0, stopping the servo, and cleaning up the GPIO pins.
    """
    servo1.ChangeDutyCycle(0)
    servo1.stop()
    GPIO.cleanup()