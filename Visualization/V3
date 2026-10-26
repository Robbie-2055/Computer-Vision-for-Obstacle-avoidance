# V3: Region Of Interest
# 
# Objective: This script integrates YOLO object detection 
#           with video processing to identify and visualize 
#           specific regions of interest (like paths) in a video feed. It uses the 
#           YOLO model to generate masks for detected objects 
#           and overlays these masks on the original video 
#           frames for better visualization. Additionally, 
#           it draws static reference lines and crops 
#           the bottom third of the frame for focused analysis.

# v3_geometry_and_cropping.py
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("train-8\\weights\\best.pt")
path_class_id = 2 
cap = cv2.VideoCapture("Training\\Image_of _Car_POV.mp4")

while True:
    ret, frame = cap.read()
    if not ret: break
        
    height, width, _ = frame.shape
    center_x = width // 2
    crop_y_start = int(height * (2/3))
    
    visual_frame = frame.copy()
    
    # NEW: Draw static reference lines
    cv2.line(visual_frame, (center_x, 0), (center_x, height), (255, 0, 0), 2)
    cv2.line(visual_frame, (0, crop_y_start), (width, crop_y_start), (0, 255, 255), 2)
    
    results = model.predict(frame, imgsz=320, verbose=False)
    path_found = False
    
    if results[0].masks is not None:
        binary_mask = np.zeros((height, width), dtype=np.uint8)
        masks = results[0].masks.data.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        
        for i, cls in enumerate(classes):
            if int(cls) == path_class_id:
                mask_resized = cv2.resize(masks[i], (width, height))
                binary_mask[mask_resized > 0.5] = 255
                path_found = True
                
        if path_found:
            colored_mask = np.zeros_like(frame)
            colored_mask[binary_mask == 255] = [0, 255, 0]
            cv2.addWeighted(colored_mask, 0.4, visual_frame, 1.0, 0, visual_frame)
            
            # NEW: Crop to the bottom third 
            bottom_crop = binary_mask[crop_y_start:height, :]
            
    cv2.imshow("Autonomous Vision Debugger", visual_frame)
    # NEW: Show the raw binary mask window
    if path_found:
        cv2.imshow("Raw Binary Mask", binary_mask)
        
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()