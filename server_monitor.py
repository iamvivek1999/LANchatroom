import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'  # listen on all interfaces
PORT = 12345

clients = {}  # {conn: username}

def broadcast(message, sender_conn=None):
    """Send message to all clients except sender."""
    for client in list(clients.keys()):
        if client != sender_conn:
            try:
                client.send(message.encode())
            except:
                client.close()
                del clients[client]

def handle_client(conn, addr):
    try:
        # First message from client is the username
        username = conn.recv(1024).decode().strip()
        clients[conn] = username
        join_time = datetime.now().strftime("%H:%M:%S")
        print(f"[{join_time}] 📢 {username} joined from {addr}")
        broadcast(f"📢 {username} joined the chat!", conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            time_stamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{time_stamp}] {username}: {msg}")

            if msg.lower() == "bye":
                conn.send("You left the chat.".encode())
                break

            broadcast(f"{username}: {msg}", conn)

    except Exception as e:
        print(f"[ERROR] {addr} -> {e}")

    finally:
        leave_time = datetime.now().strftime("%H:%M:%S")
        print(f"[{leave_time}] ❌ {clients.get(conn, 'Unknown')} left the chat.")
        broadcast(f"❌ {clients.get(conn, 'Unknown')} left the chat.")
        if conn in clients:
            del clients[conn]
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"💬 Server monitoring chat on {HOST}:{PORT}...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
