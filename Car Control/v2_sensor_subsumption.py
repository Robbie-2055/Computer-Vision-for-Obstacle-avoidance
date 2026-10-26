#V2: Sensor reflex Layer
# 
# Objective: : Implement the 8-sensor spatial awareness. 
#             The car will blindly drive forward until a sensor 
#             trips, at which point it will execute the 
#             appropriate reflex (stop, reverse, pivot, or veer)
#             based on our priority list.


# v2_8sensor_subsumption.py
import Jetson.GPIO as GPIO
import time

# ==========================================
# 1. HARDWARE & PIN SETUP
# ==========================================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor Pins
ENA, IN1, IN2 = 12, 5, 6
ENB, IN3, IN4 = 13, 16, 19

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
# 3. EVASION LOGIC (SUBSUMPTION LAYER)
# ==========================================
def handle_subsumption_layer():
    """
    Reads sensors and executes evasive maneuvers.
    Returns True if an evasion occurred, False if the path is clear.
    """
    # Read pins (True = Object Detected)
    fc = GPIO.input(SENS_FC) == GPIO.LOW
    fl = GPIO.input(SENS_FL) == GPIO.LOW
    fr = GPIO.input(SENS_FR) == GPIO.LOW
    ml = GPIO.input(SENS_ML) == GPIO.LOW
    mr = GPIO.input(SENS_MR) == GPIO.LOW
    rc = GPIO.input(SENS_RC) == GPIO.LOW
    
    # Priority 1: Head-on Collision (Requires stop & escape)
    if fc:
        print("REFLEX: Front blocked! Stopping.")
        set_motors(0, 0)
        time.sleep(0.1)
        
        # Check blindspot before reversing
        if not rc:
            print("REFLEX: Reversing...")
            set_motors(50, 50, reverse=True)
            time.sleep(0.5)
            
        # Pivot away from side clutter
        if fl or ml:
            pivot("right", 60, 0.5)
        else:
            pivot("left", 60, 0.5)
        return True

    # Priority 2: Corner Glancing (Veer away without stopping)
    if fl:
        print("REFLEX: Front-Left trigger. Veering Right.")
        set_motors(60, 20) 
        time.sleep(0.2)
        return True
    elif fr:
        print("REFLEX: Front-Right trigger. Veering Left.")
        set_motors(20, 60)
        time.sleep(0.2)
        return True
        
    # Priority 3: Side Proximity (Gentle nudge to re-center)
    if ml:
        print("REFLEX: Left side close. Nudging Right.")
        set_motors(50, 30)
        time.sleep(0.1)
        return True
    elif mr:
        print("REFLEX: Right side close. Nudging Left.")
        set_motors(30, 50)
        time.sleep(0.1)
        return True

    # No sensors triggered
    return False 

# ==========================================
# 4. BLIND AUTONOMOUS LOOP
# ==========================================
try:
    print("Starting Blind Evasion Test...")
    while True:
        is_evading = handle_subsumption_layer()
        
        if not is_evading:
            # If no sensors are triggered, just drive forward
            set_motors(40, 40)
            
        time.sleep(0.05) # Small delay to stabilize sensor readings

except KeyboardInterrupt:
    print("Program stopped.")

finally:
    # [INCLUDE V1 CLEANUP HERE]
    pass