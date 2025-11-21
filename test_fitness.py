import neato_client
import time

def test_fitness():
    bridge = neato_client.NeatoBridge()
    if not bridge.connect():
        return

    print("Connected! Move Mario around. Press Ctrl+C to stop.")
    
    try:
        while True:
            frame = bridge.get_state() # This updates variables internally
            if frame is not None:
                print(f"Pos: ({bridge.mario_x}, {bridge.mario_y}) | Mode: {bridge.game_mode} | Level: {bridge.level_index} | Timer: {bridge.end_level_timer} | Anim: {bridge.anim_state}")
                
                if bridge.anim_state == 9:
                    print(">>> MARIO DIED <<<")
                if bridge.end_level_timer > 0:
                    print(">>> LEVEL COMPLETE! <<<")
            else:
                print("Failed to get state.")
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")
        bridge.close()

if __name__ == "__main__":
    test_fitness()
