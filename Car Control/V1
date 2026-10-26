#V1: Motor Control Test
# 
# Objective: This script is designed to test the motor 
#           control of a robotic car using the Jetson GPIO 
#           library. It sets up the GPIO pins for motor control,
#           initializes PWM for speed control, and provides a 
#           function to set the speed and direction of the 
#           motors. The script includes a test sequence to run 
#           the motors forward and backward at 50% speed, and 
#           ensures that the motors are stopped and GPIO 
#           resou1rces are cleaned up when the script exits.

# v1_8sensor_hardware_test.py
import Jetson.GPIO as GPIO
import time

# ==========================================
# 1. HARDWARE & PIN SETUP
# ==========================================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor Pins
ENA, IN1, IN2 = 32, 29, 31
ENB, IN3, IN4 = 33, 35, 37

# 8-Sensor Pin Layout
SENS_FC, SENS_FL, SENS_FR = 26, 20, 21  # Front row
SENS_ML, SENS_MR = 17, 27               # Mid row
SENS_RC, SENS_RL, SENS_RR = 22, 23, 24  # Rear row
SENSOR_PINS = [SENS_FC, SENS_FL, SENS_FR, SENS_ML, SENS_MR, SENS_RC, SENS_RL, SENS_RR]

# Setup GPIO
GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)
GPIO.setup(SENSOR_PINS, GPIO.IN) # Sensors pull LOW when an object is near

# Initialize PWM
pwm_left = GPIO.PWM(ENA, 100)
pwm_right = GPIO.PWM(ENB, 100)
pwm_left.start(0)
pwm_right.start(0)

# ==========================================
# 2. MOVEMENT API
# ==========================================
def set_motors(left_speed, right_speed, reverse=False):
    """Handles standard forward and reverse driving with clamped speeds."""
    left_speed = max(0, min(100, left_speed))
    right_speed = max(0, min(100, right_speed))
    
    if reverse:
        GPIO.output([IN1, IN3], GPIO.LOW)
        GPIO.output([IN2, IN4], GPIO.HIGH)
    else:
        GPIO.output([IN1, IN3], GPIO.HIGH)
        GPIO.output([IN2, IN4], GPIO.LOW)
        
    pwm_left.ChangeDutyCycle(left_speed)
    pwm_right.ChangeDutyCycle(right_speed)

def pivot(direction, speed=60, duration=0.3):
    """Spins the chassis in place by driving wheels in opposite directions."""
    if direction == "right":
        GPIO.output([IN1, IN4], GPIO.HIGH)
        GPIO.output([IN2, IN3], GPIO.LOW)
    elif direction == "left":
        GPIO.output([IN1, IN4], GPIO.LOW)
        GPIO.output([IN2, IN3], GPIO.HIGH)
        
    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)
    time.sleep(duration)
    set_motors(0, 0) # Stop after pivoting

# ==========================================
# 3. HARDWARE TEST LOOP
# ==========================================
try:
    print("Testing Motors: Driving Forward...")
    set_motors(40, 40)
    time.sleep(1)
    
    print("Testing Motors: Pivoting Right...")
    pivot("right", speed=50, duration=1.0)
    
    print("Testing Motors: Pivoting Left...")
    pivot("left", speed=50, duration=1.0)

except KeyboardInterrupt:
    print("Test aborted.")

finally:
    # Always turn off motors on exit
    set_motors(0, 0)
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
    print("Hardware cleaned up.")