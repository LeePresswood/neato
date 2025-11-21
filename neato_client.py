import socket
import time

class NeatoBridge:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.sock = None

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
            self.sock.sendall((command + "\n").encode('utf-8'))
            response = self.sock.recv(4096).decode('utf-8').strip()
            return response
        except Exception as e:
            print(f"Error sending command: {e}")
            self.sock.close()
            self.sock = None
            return None

    def get_state(self):
        return self.send_command("GET_STATE")

    def act(self, action):
        return self.send_command("ACT")

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
