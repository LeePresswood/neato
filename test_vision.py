import neato_client
import cv2
import time

def test_vision():
    bridge = neato_client.NeatoBridge()
    if not bridge.connect():
        return

    print("Connected! Capturing screen in 3 seconds...")
    time.sleep(3)
    
    frame = bridge.get_state()
    
    if frame is not None:
        print(f"Captured frame shape: {frame.shape}")
        cv2.imwrite("test_capture.png", frame)
        print("Saved 'test_capture.png'. Check if it looks right!")
    else:
        print("Failed to capture frame.")
        
    bridge.close()

if __name__ == "__main__":
    test_vision()
