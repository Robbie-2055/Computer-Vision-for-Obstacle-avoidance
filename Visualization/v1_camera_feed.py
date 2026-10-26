# V1: Camera Feed Display
# 
# Objective: This script displays a live camera 
#            feed in a window.

# v1_camera_feed.py
import cv2

# Setup video capture
cap = cv2.VideoCapture("Image_of _Car_POV.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video.")
        break
        
    # Show the raw frame
    cv2.imshow("Autonomous Vision Debugger", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()