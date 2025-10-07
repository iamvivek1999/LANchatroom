import socket
import threading
import streamlit as st
import time

# --- Globals ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sock" not in st.session_state:
    st.session_state.sock = None
if "connected" not in st.session_state:
    st.session_state.connected = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Functions ---
def connect_to_server(ip, port, username):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        st.session_state.sock = s
        st.session_state.connected = True
        st.session_state.username = username
        s.send(username.encode())
        threading.Thread(target=receive_messages, args=(s,), daemon=True).start()
        st.session_state.messages.append(f"✅ Connected to {ip}:{port} as {username}")
    except Exception as e:
        st.session_state.messages.append(f"❌ Connection failed: {e}")

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            st.session_state.messages.append(msg)
            time.sleep(0.1)
            st.experimental_rerun()
        except:
            break

def send_message():
    text = st.session_state.input_text
    if text.strip() == "":
        return
    try:
        st.session_state.sock.send(text.encode())
        st.session_state.messages.append(f"You: {text}")
    except:
        st.session_state.messages.append("⚠️ Disconnected from server.")
        st.session_state.connected = False
    st.session_state.input_text = ""

# --- Streamlit UI ---
st.title("💬 LAN Chat Client")

if not st.session_state.connected:
    ip = st.text_input("Server IP", "10.25.19.135")
    port = st.number_input("Port", 12345, step=1)
    username = st.text_input("Your Name")
    if st.button("Connect") and username.strip() != "":
        connect_to_server(ip, port, username)
else:
    st.success(f"Connected as {st.session_state.username}")

# Chat history
st.subheader("Chat History")
chat_box = st.empty()
for m in st.session_state.messages[-50:]:
    st.write(m)

# Message input
if st.session_state.connected:
    st.text_input("Type a message", key="input_text", on_change=send_message)
