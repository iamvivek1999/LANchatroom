import streamlit as st
import socket
import threading
import time

# -------------------
# Initialize session state
# -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sock" not in st.session_state:
    st.session_state.sock = None
if "connected" not in st.session_state:
    st.session_state.connected = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------
# Functions
# -------------------
def connect_to_server(ip, port, username):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        st.session_state.sock = s
        st.session_state.connected = True
        st.session_state.username = username
        s.send(username.encode())  # send username immediately
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
            time.sleep(0.05)
        except:
            break

def send_message(text):
    if text.strip() == "":
        return
    try:
        st.session_state.sock.send(text.encode())
        st.session_state.messages.append(f"You: {text}")
    except:
        st.session_state.messages.append("⚠️ Disconnected from server.")
        st.session_state.connected = False

# -------------------
# Streamlit UI
# -------------------
st.set_page_config(page_title="LAN Chat", layout="wide")
st.title("💬 LAN Chat Client (Enhanced)")

# Connection panel
with st.sidebar:
    st.header("Connect to Server")
    if not st.session_state.connected:
        ip = st.text_input("Server IP", "10.25.19.135")
        port = st.number_input("Port", 12345, step=1)
        username = st.text_input("Your Name")
        if st.button("Connect") and username.strip() != "":
            connect_to_server(ip, port, username)
    else:
        st.success(f"Connected as {st.session_state.username}")
        if st.button("Disconnect"):
            st.session_state.sock.close()
            st.session_state.connected = False
            st.session_state.messages.append("❌ You disconnected.")

# Chat panel
st.subheader("Chat History")
chat_container = st.container()

# Message input
if st.session_state.connected:
    text = st.text_input("Type a message", key="input_text")
    if st.button("Send") and text.strip() != "":
        send_message(text)
        st.experimental_rerun()  # update messages instantly

# Render messages
with chat_container:
    for msg in st.session_state.messages[-100:]:
        if msg.startswith(f"You:"):
            st.markdown(f"<p style='text-align: right; color: blue;'>{msg}</p>", unsafe_allow_html=True)
        elif "joined the chat" in msg or "left the chat" in msg:
            st.markdown(f"<p style='text-align: center; color: green;'>{msg}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: left; color: black;'>{msg}</p>", unsafe_allow_html=True)
