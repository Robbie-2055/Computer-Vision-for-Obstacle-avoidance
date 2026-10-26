# Autonomous Robotic Car: Vision Pipeline, Sensor Reflexes, & Full AI Stack

An end-to-end repository combining a **computer vision and path detection pipeline** with an **NVIDIA Jetson hardware and sensor reflex stack** to build a obstacle avoidance pipeline.

---

## 🚀 Project Architecture & Progression

The project is structured into two main tracks: **Vision Processing & Navigation Math** and **Hardware Motor Control & Subsumption Reflexes**.

### Track 1: Vision Pipeline & Navigation Debugger
* **V1: Camera Feed Display (`v1_camera_feed.py`)**  
  * Displays a raw live video or camera feed in a window to verify input capability.
* **V2: YOLO Integration & Visual Masking (`v2_yolo_masking.py`)**  
  * Integrates the YOLO model to generate instance segmentation masks for detected objects.
  * Filters for the target path class and overlays a semi-transparent green tint on the detected path.
* **V3: Region of Interest (ROI) & Geometry (`v3_geometry_and_cropping.py`)**  
  * Introduces static reference lines (a vertical center line and a horizontal line marking the bottom-third boundary).
  * Crops the bottom third of the binary mask to isolate the immediate path ahead for focused analysis.
* **V4: Autonomous Vision Debugger with Navigation Math (`v4_autonomous_vision_debugger.py`)**  
  * Calculates image moments on the cropped binary mask to find the path's centroid $(cx, cy)$.
  * Computes raw and normalized error metrics relative to the frame's center.
  * Generates real-time simulated steering commands (`STRAIGHT`, `LEFT`, `RIGHT`) and overlays visual debugging cues.

**Sample Result**
  <img width="1903" height="966" alt="image" src="https://github.com/user-attachments/assets/d4363f3e-8346-46e3-a9e7-c0f4b37fa2cb" />




### Track 2: Hardware, Sensors, & Full Stack Integration
* **V1: Motor Control & Hardware Test (`v1_8sensor_hardware_test.py`)**  
  * Tests the motor control of a robotic car using the Jetson GPIO library.
  * Sets up GPIO pins for motor control and initializes PWM for speed control.
  * Provides movement functions and a test sequence running motors forward and backward.
  * Ensures motors stop and GPIO resources are cleaned up upon script exit.
* **V2: Sensor Reflex Layer (`v2_8sensor_subsumption.py`)**  
  * Implements 8-sensor spatial awareness where the car blindly drives forward until a sensor trips.
  * Executes appropriate reflexes—such as stopping, reversing, pivoting, or veering—based on a strict priority list.
* **V3: Full Autonomous Stack (`v3_full_8sensor_vision_integration.py`)**  
  * Integrates the 8-sensor reflex layer with YOLO-based vision processing to create a fully autonomous robotic car.
  * Prioritizes immediate sensor-based evasive maneuvers over AI-driven path following to guarantee safety and responsiveness in dynamic environments.

---

## ⚙️ Hardware & Pin Configuration

The platform utilizes the Jetson GPIO library configured in BCM mode.

### 8-Sensor Pin Layout
* **Front Row:** Center (`SENS_FC`: Pin 26), Left (`SENS_FL`: Pin 20), Right (`SENS_FR`: Pin 21).
* **Mid Row:** Left (`SENS_ML`: Pin 17), Right (`SENS_MR`: Pin 27).
* **Rear Row:** Center (`SENS_RC`: Pin 22), Left (`SENS_RL`: Pin 23), Right (`SENS_RR`: Pin 24).
* **Sensor Behavior:** Sensors pull `LOW` when an object is near.

### Motor Pins & PWM Setup
* **Hardware Test Pin Mapping (V1):** Motor pins include `ENA, IN1, IN2 = 32, 29, 31` and `ENB, IN3, IN4 = 33, 35, 37` with PWM initialized at 100 Hz.
* **Autonomous Stack Pin Mapping (V2 & V3):** Motor pins are configured to `ENA, IN1, IN2 = 12, 5, 6` and `ENB, IN3, IN4 = 13, 16, 19` with PWM running at 100 Hz.

---

## 🧠 Subsumption Reflex Hierarchy

The sensor reflex layer evaluates environmental obstacles using a prioritized decision tree:
* **Priority 1 (Head-on Collision):** Triggered by `SENS_FC`. The car stops, checks the rear blindspot (`SENS_RC`), reverses if clear, and pivots away from side clutter.
* **Priority 2 (Corner Glancing):** Triggered by front-left (`SENS_FL`) or front-right (`SENS_FR`) sensors. The car veers away instantly without coming to a full stop.
* **Priority 3 (Side Proximity):** Triggered by mid-left (`SENS_ML`) or mid-right (`SENS_MR`) sensors. The car applies a gentle nudge to re-center itself.

---

## 🛠️ Prerequisites & Installation

To run the full hardware and vision software stack on an NVIDIA Jetson platform, install the required dependencies:

```bash
pip install Jetson.GPIO opencv-python numpy ultralytics
```

---

## 💻 Setup & Execution Guidelines

1. Place your trained YOLO model weights at `train-8\weights\best.pt` (or `best.engine` for optimized Jetson deployment).
2. Provide test video inputs (e.g., `Training\Image_of _Car_POV.mp4`) or configure video capture to use a live camera feed (`0`).
3. Run the target script depending on your current testing phase:

```bash
# Test basic motor controls and hardware wiring
python v1_8sensor_hardware_test.py

# Run sensor-only reflexive evasion
python v2_8sensor_subsumption.py

# Run the complete computer vision debugging pipeline
python v4_autonomous_vision_debugger.py

# Launch the full autonomous stack (YOLO vision + sensor reflex layer)
python v3_full_8sensor_vision_integration.py
```

* **Controls:** Press **`q`** while any OpenCV visualization window is active to quit the application.
