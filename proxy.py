import socket
import threading

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen(5)
    server.settimeout(1)
    print("[*] Listening on 0.0.0.0:8888")

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

start_proxy()

    
    