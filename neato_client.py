import socket
import time
import mss
import cv2
import numpy as np

class NeatoBridge:
    def __init__(self, host='127.0.0.1', port=8086):
        self.host = host
        self.port = port
        self.sock = None
        self.mario_x = 0
        self.mario_y = 0
        self.game_mode = 0
        self.level_index = 0
        self.end_level_timer = 0
        self.anim_state = 0

    def connect(self):
        """Connects to the Bizhawk Lua server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"Connected to Bizhawk at {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print("Connection refused. Is Bizhawk running with neato_bridge.lua?")
            return False

    def send_command(self, command):
        """Sends a command to the server and waits for a response."""
        if not self.sock:
            print("Not connected.")
            return None

        try:
            self.sock.sendall((command + "\r\n").encode('utf-8'))
            response = self.sock.recv(4096).decode('utf-8').strip()
            return response
        except Exception as e:
            print(f"Error sending command: {e}")
            self.sock.close()
            self.sock = None
            return None

    def get_state(self):
        """
        Returns the current game screen as a numpy array.
        """
        response = self.send_command("GET_STATE")
        if not response:
            return None
            
        try:
            # Parse coordinates: x, y, w, h, bx, by, mx, my, mode, level, timer, anim
            parts = list(map(int, response.split(',')))
            x, y, w, h, bx, by, mx, my, mode, level, timer, anim = parts
            
            # Update game state
            self.mario_x = mx
            self.mario_y = my
            self.game_mode = mode
            self.level_index = level
            self.end_level_timer = timer
            self.anim_state = anim
            
            # Calculate capture region
            # These values might need tuning based on the user's OS/theme.
            TITLE_BAR_HEIGHT = 25
            MENU_BAR_HEIGHT = 20
            BORDER_WIDTH = 8
            
            # If the API returned valid border info, use it, otherwise use defaults
            offset_y = by if by > 0 else (TITLE_BAR_HEIGHT + MENU_BAR_HEIGHT + BORDER_WIDTH)
            offset_x = bx if bx > 0 else BORDER_WIDTH
            
            monitor = {
                "top": y + offset_y, 
                "left": x + offset_x, 
                "width": w,
                "height": h
            }
            
            with mss.mss() as sct:
                # Capture the screen
                img = np.array(sct.grab(monitor))
                
                # Drop alpha channel (BGRA -> BGR)
                img = img[:, :, :3]
                
                # Resize to a standard input size (e.g., 128x112 - half SNES)
                # This keeps the neural network input manageable
                img_small = cv2.resize(img, (128, 112))
                
                return img_small
                
                
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def act(self, buttons):
        """
        Sends button states to the Lua script.
        buttons: dict of 'BUTTON_NAME': boolean
        """
        # Format: "ACT:A,B,Up" (comma separated list of pressed buttons)
        pressed = [k for k, v in buttons.items() if v]
        if pressed:
            cmd = "ACT:" + ",".join(pressed)
        else:
            cmd = "ACT:"  # No buttons pressed
        
        response = self.send_command(cmd)
        return response == "ACT_OK"

    def reset(self):
        return self.send_command("RESET")

    def close(self):
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    # Simple test
    bridge = NeatoBridge()
    if bridge.connect():
        print("Response from GET_STATE:", bridge.get_state())
        time.sleep(1)
        print("Response from ACT:", bridge.act("A"))
        bridge.close()
