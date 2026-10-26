# V2: Yolo Integration and Visual Masking
# 
# Objective:This script integrates YOLO object detection 
#           with video processing to identify and visualize 
#           specific (like paths) in a video feed. It uses the 
#           YOLO model to generate masks for detected objects 
#           and overlays these masks on the original video 
#           frames for better visualization.


# v2_yolo_masking.py
import cv2
import numpy as np
from ultralytics import YOLO

# Load model and find path class
model = YOLO("train-8\\weights\\best.pt")
path_class_id = 2 # Assuming 2 based on your fallback

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
        
    height, width, _ = frame.shape
    visual_frame = frame.copy()
    
    # Run YOLO
    results = model.predict(frame, imgsz=320, verbose=False)
    
    if results[0].masks is not None:
        binary_mask = np.zeros((height, width), dtype=np.uint8)
        masks = results[0].masks.data.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        
        for i, cls in enumerate(classes):
            if int(cls) == path_class_id:
                mask_resized = cv2.resize(masks[i], (width, height))
                binary_mask[mask_resized > 0.5] = 255
                
                # Create a green tint for visualization
                colored_mask = np.zeros_like(frame)
                colored_mask[binary_mask == 255] = [0, 255, 0]
                cv2.addWeighted(colored_mask, 0.4, visual_frame, 1.0, 0, visual_frame)

    cv2.imshow("Autonomous Vision Debugger", visual_frame)
    cv2.imshow("Raw Binary Mask", binary_mask)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()