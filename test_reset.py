import neato_client
import time

bridge = neato_client.NeatoBridge()

if bridge.connect():
    print("Connected!")
    
    # Test reset 5 times
    for i in range(5):
        print(f"\n--- Reset {i+1} ---")
        bridge.reset()
        time.sleep(0.5)
        
        # Get state
        img = bridge.get_state()
        if img is not None:
            print(f"Mario X: {bridge.mario_x}")
            print(f"Mario Y: {bridge.mario_y}")
            print(f"Game Mode: {bridge.game_mode}")
        else:
            print("Failed to get state!")
        
        time.sleep(1)
    
    bridge.close()
else:
    print("Failed to connect!")
