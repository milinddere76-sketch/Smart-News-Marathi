import socket
import sys

def test_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))
        s.listen(1)
        print(f"SUCCESS: Port {port} is available and listening.")
        s.close()
    except Exception as e:
        print(f"FAILURE: Port {port} could not be opened. Error: {e}")

if __name__ == "__main__":
    test_port(8000)
    test_port(8001)
    test_port(8080)
