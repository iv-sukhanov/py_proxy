import socket
import threading
import argparse

def start_proxy(host: str, ports: int, connections: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, ports))
    server.listen(connections)
    server.settimeout(1)
    print(f"[*] Listening on {host}:{ports}")

    client_threads = []

    try:
        while True:
            try:
                client_socket, addr = server.accept()
                print(f"[*] Accepted connection from {addr}")
                client_handler = threading.Thread(
                    target=handle_client,
                    args=(client_socket, addr)
                )
                client_handler.daemon = True
                client_threads.append(client_handler)
                client_handler.start()
            except socket.timeout:
                pass
            except Exception as e:
                print(f"[*] Error accepting connection: {e}")
    except KeyboardInterrupt:
        print("\n[*] Shutting down the proxy server...")
    finally:
        print("[*] Closing server socket and cleaning up...")
        server.close()
        
        for thread in client_threads:
            thread.join(timeout=1.0)
        
        print("[*] Server shutdown complete.")
        
def handle_client(client_socket, addr):
    request = client_socket.recv(4096)

    lines = request.split(b'\r\n')
    for line in lines:
        if line.startswith(b'Host:'):
            host = line.split(b': ')[1]
            break
    
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((host, 80))
    print(f"[*] Forwarding request to {host.decode()}")
    remote_socket.send(request)

    while True:
        response = remote_socket.recv(4096)
        if len(response) == 0:
            break
        print(f"[*] Received response from: {host.decode()}")
        print(f"[*] Sending response to: {addr}")
        client_socket.send(response)


    client_socket.close()
    remote_socket.close()

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Simple Python Proxy Server")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the proxy server to')
    parser.add_argument('--ports', type=int, default=8888, help='Port to bind the proxy server to')
    parser.add_argument('--connections', type=int, default=5, help='Maximum number of simultaneous connections (backlog)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"[*] Starting proxy server on {args.host}:{8888} with a backlog of {args.connections}")
    start_proxy(args.host, args.ports, args.connections)

    
    