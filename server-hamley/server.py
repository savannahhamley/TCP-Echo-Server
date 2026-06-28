import os
import socket
import sys
import threading  # 1. Added: Import the threading module to handle concurrent clients
from typing import Tuple

# Retrieve configurations from Docker environment variables
USERNAME = os.getenv("STUDENT_USERNAME") 
HOST = "0.0.0.0" 
PORT = int(os.getenv("APP_PORT"))

def create_listen_socket(host: str, port: int) -> socket.socket:
    """Create, bind, and listen on a TCP socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    return s

def handle_client(conn: socket.socket, addr: Tuple[str, int]) -> None:
    """Echo loop for a single client - this now runs in its own thread."""
    print(f"[server:{USERNAME}] connection from {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data: 
                break
            print(f"[server:{USERNAME}] received from {addr}: {data.decode()!r}")
            conn.sendall(data)
    finally:
        conn.close()
        print(f"[server:{USERNAME}] connection from {addr} closed")

def main() -> None: 
    try:
        lsock = create_listen_socket(HOST, PORT)
    except Exception as e:
        print(f"[server:{USERNAME}] failed to create listen socket: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[server:{USERNAME}] listening on {HOST}:{PORT}")
    
    while True:
        try:
            # Wait for a new client connection
            conn, addr = lsock.accept()
            
            # 2. Changed: Instead of calling handle_client directly (which blocks), 
            # we create a new thread for this specific connection.
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            
            # 3. Added: Mark as daemon so threads close automatically when the server stops
            client_thread.daemon = True 
            
            # 4. Added: Start the thread
            client_thread.start()
            
            # Log active threads to prove concurrency
            print(f"[server:{USERNAME}] Active client threads: {threading.active_count() - 1}")
            
        except KeyboardInterrupt:
            print("\n[server] shutting down.")
            break
        except Exception as e:
            print(f"[server:{USERNAME}] error: {e}", file=sys.stderr)
    lsock.close()

if __name__ == "__main__":
    main()