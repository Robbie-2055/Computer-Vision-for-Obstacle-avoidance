#V3: Full Autonomous Stack
# 
# Objective: This script integrates the 8-sensor reflex layer 
#           with YOLO-based vision processing to create a 
#           fully autonomous robotic car. The car will 
#           prioritize immediate sensor-based evasive 
#           maneuvers over AI-driven path following, 
#           ensuring safety and responsiveness in dynamic 
#           environments.

# v3_full_8sensor_vision_integration.py
import cv2
import numpy as np
import Jetson.GPIO as GPIO
from ultralytics import YOLO
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
# AI & VISION SETUP
# ==========================================
model = YOLO("best.engine") 
cap = cv2.VideoCapture(0)

BASE_SPEED = 40  
Kp = 35          

# ==========================================
# MAIN PIPELINE LOOP
# ==========================================
try:
    print("Starting Full Autonomous Stack...")
    while True:
        ret, frame = cap.read()
        if not ret: break
            
        # ------------------------------------------
        # LAYER 1: HARDWARE REFLEXES
        # ------------------------------------------
        # If an obstacle is nearby, handle it and skip AI processing
        is_evading = handle_subsumption_layer()
        if is_evading:
            continue 
            
        # ------------------------------------------
        # LAYER 2: YOLO VISION
        # ------------------------------------------
        results = model.predict(frame, imgsz=320, verbose=False)
        height, width, _ = frame.shape
        center_x = width // 2
        floor_found = False

        if results[0].masks is not None:
            # Initialize empty binary canvas
            binary_mask = np.zeros((height, width), dtype=np.uint8)
            masks = results[0].masks.data.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            
            for i, cls in enumerate(classes):
                # Class 0 = "Floor" or "Path"
                if int(cls) == 0:  
                    mask_resized = cv2.resize(masks[i], (width, height))
                    binary_mask[mask_resized > 0.5] = 255 # Binarize confident pixels
                    floor_found = True

            if floor_found:
                # ------------------------------------------
                # LAYER 3: SPATIAL MATH
                # ------------------------------------------
                # Look only at the bottom 1/3 of the screen
                crop_y_start = int(height * (2/3))
                bottom_crop = binary_mask[crop_y_start:height, :]
                
                # Find the center of mass (centroid) of the white pixels
                M = cv2.moments(bottom_crop)
                
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    
                    # ------------------------------------------
                    # LAYER 4: STEERING CONTROL
                    # ------------------------------------------
                    # Calculate how far off-center the path is (-1.0 to 1.0)
                    error_raw = cx - center_x
                    error_norm = error_raw / center_x  
                    
                    # Adjust motor speeds based on the error
                    pwm_l = BASE_SPEED + (error_norm * Kp)
                    pwm_r = BASE_SPEED - (error_norm * Kp)
                    
                    set_motors(pwm_l, pwm_r, reverse=False)
                else:
                    # AI sees the floor, but not immediately in front of the car
                    set_motors(0, 0)
        else:
            # AI cannot see the floor anywhere
            set_motors(0, 0)

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    # [INCLUDE V1 CLEANUP HERE]
    cap.release()