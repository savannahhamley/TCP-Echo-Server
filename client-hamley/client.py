import os
import socket
import sys
import time

# Retrieve credentials and connection details from Docker environment
USERNAME = os.getenv("STUDENT_USERNAME") or "Unknown"
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
CONNECT_TIMEOUT = 5 

def connect_once(host: str, port: int) -> socket.socket:
    """Create a TCP connection to the server."""
    # create_connection handles both the socket creation and the 3-way handshake
    return socket.create_connection((host, port), timeout=CONNECT_TIMEOUT)

def main() -> None:
    print(f"[client:{USERNAME}] target → {SERVER_HOST}:{SERVER_PORT}")
    try:
        sock = connect_once(SERVER_HOST, SERVER_PORT)
    except Exception as e:
        print(f"[client:{USERNAME}] connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[client:{USERNAME}] connected. Type messages; Ctrl+C to quit.")
    try:
        while True:
            # Take interactive user input from the terminal
            message = input("> ")

            # Prepend username so the traffic is identifiable in Wireshark logs
            full_message = f"{USERNAME}: {message}"

            # Convert string to bytes before sending over the network
            sock.sendall(full_message.encode())
        
            # Receive the echoed response from the server
            data = sock.recv(4096)

            print(f"[echo] {data.decode()}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[client] exiting.")
    finally:
        # Close the socket to trigger the FIN/ACK sequence in Wireshark
        sock.close()

if __name__ == "__main__":
    main()