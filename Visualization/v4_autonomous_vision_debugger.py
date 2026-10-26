#V4: Autonomous Vision Debugger with Navigation Math
#
#Objective: This script integrates YOLO object detection 
#           with video processing to identify and visualize 
#           specific objects (like paths) in a video feed. 
#           It calculates navigation math based on the detected 
#           path's centroid, providing real-time feedback for
#           autonomous navigation. The script overlays visual 
#           cues, including reference lines, centroid markers, 
#           and error metrics, on the original video frames 
#           for enhanced debugging and analysis.

# v4_autonomous_vision_debugger.py
import cv2
import numpy as np
from ultralytics import YOLO

# ==========================================
# 1. SETUP
# ==========================================
# Use .engine for Jetson, or .pt if testing on a laptop/PC
model = YOLO("train-8\\weights\\best.pt")

# Find the Path class ID from the model labels
path_class_id = None
for cid, name in model.names.items():
    if str(name).strip().lower() == "path":
        path_class_id = int(cid)
        break
if path_class_id is None:
    path_class_id = 2  # fallback if the label is missing
print(f"Using path class id: {path_class_id}, name: {model.names.get(path_class_id, 'unknown')}")

# Use 0 for webcam, or replace with "test_video.mp4" to test offline
cap = cv2.VideoCapture("Training\\Image_of _Car_POV.mp4")

print("Starting Vision Pipeline Test...")
print("Press 'q' to quit.")

# ==========================================
# 2. MAIN VISUALIZATION LOOP
# ==========================================

cv2.namedWindow("Autonomous Vision Debugger", cv2.WINDOW_NORMAL)
# Fullscreen removed to keep the window resizable and non-blocking

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame or end of video.")
        break
        
    height, width, _ = frame.shape
    center_x = width // 2
    crop_y_start = int(height * (2/3))
    
    # Run YOLO inference
    results = model.predict(frame, imgsz=320, verbose=False)
    
    # Create a blank overlay for visualizations
    visual_frame = frame.copy()
    
    # Draw static reference lines
    # Vertical line representing the dead-center of the camera
    cv2.line(visual_frame, (center_x, 0), (center_x, height), (255, 0, 0), 2)
    # Horizontal line representing the start of the bottom-third crop area
    cv2.line(visual_frame, (0, crop_y_start), (width, crop_y_start), (0, 255, 255), 2)
    
    path_found = False

    if results[0].masks is not None:
        binary_mask = np.zeros((height, width), dtype=np.uint8)
        
        masks = results[0].masks.data.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        
        for i, cls in enumerate(classes):
            if int(cls) == path_class_id:  # Use the Path class from the model labels
                mask_resized = cv2.resize(masks[i], (width, height))
                binary_mask[mask_resized > 0.5] = 255
                path_found = True

        if path_found:
            # Create a green tint where the path is detected
            colored_mask = np.zeros_like(frame)
            colored_mask[binary_mask == 255] = [0, 255, 0]
            
            # Blend the original frame with the green path mask
            cv2.addWeighted(colored_mask, 0.4, visual_frame, 1.0, 0, visual_frame)

            # Crop to the bottom third for navigation math
            bottom_crop = binary_mask[crop_y_start:height, :]
            
            # Calculate moments
            M = cv2.moments(bottom_crop)
            
            if M["m00"] > 0:
                # Calculate X and Y of the centroid relative to the cropped area
                cx = int(M["m10"] / M["m00"])
                cy_crop = int(M["m01"] / M["m00"])
                
                # Map the Y coordinate back to the full frame for visualization
                cy = cy_crop + crop_y_start
                
                # Calculate navigation math
                error_raw = cx - center_x
                error_norm = round(error_raw / center_x, 3) # Rounded for clean display
                
                # Draw the Centroid (Red dot)
                cv2.circle(visual_frame, (cx, cy), 10, (0, 0, 255), -1)
                
                # Draw a line from the center to the centroid to visualize the error
                cv2.line(visual_frame, (center_x, cy), (cx, cy), (0, 165, 255), 3)
                
                # Display the math on screen
                cv2.putText(visual_frame, f"Raw Error: {error_raw} px", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(visual_frame, f"Norm Error: {error_norm}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Determine simulated steering direction
                direction = "STRAIGHT"
                if error_norm > 0.15:
                    direction = "RIGHT ->"
                elif error_norm < -0.15:
                    direction = "<- LEFT"
                    
                cv2.putText(visual_frame, f"Steering: {direction}", (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)


    # Show the final visualization
    cv2.imshow("Autonomous Vision Debugger", visual_frame)
    
    # Also show the raw binary mask so you can see exactly what the math is processing
    if path_found:
        cv2.imshow("Raw Binary Mask", binary_mask)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()