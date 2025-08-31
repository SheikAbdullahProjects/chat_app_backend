import socketio

# --- Socket.IO setup ---
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["https://chat-app-frontend-ecfx.onrender.com"],
    allow_upgrades=True
)


user_socket_map = {}
socket_user_map = {}

def get_receiver_socket_id(user_id):
    """Get socket ID for a user - convert to string for consistency"""
    return user_socket_map.get(str(user_id))

async def send_new_message(receiver_id, message_data):
    """Send new message to a specific user"""
    print("Sending new message:", message_data)
    receiver_socket_id = get_receiver_socket_id(receiver_id)
    print("Receiver socket ID:", receiver_socket_id)
    
    if receiver_socket_id:
        await sio.emit("newMessage", message_data, room=receiver_socket_id)
        print(f"Message sent to user {receiver_id} on socket {receiver_socket_id}")
        return True
    else:
        print(f"User {receiver_id} is not connected")
        return False

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)
    # Extract query params
    query = environ.get("QUERY_STRING", "")
    params = dict(qc.split("=") for qc in query.split("&") if "=" in qc)
    user_id = params.get("userId")
    print("Connected userId:", user_id)

    if user_id:
        # Store as string for consistency
        user_socket_map[user_id] = sid  # This will be "2", not 2
        socket_user_map[sid] = user_id

    # Broadcast online users to all clients
    await sio.emit("getOnlineUsers", list(user_socket_map.keys()))

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
    user_id = socket_user_map.get(sid)
    

    if user_id and user_id in user_socket_map:
        del user_socket_map[user_id]

    if sid in socket_user_map:
        del socket_user_map[sid]

    # Broadcast updated list of online users
    await sio.emit("getOnlineUsers", list(user_socket_map.keys()))

@sio.event
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit("message", f"Server got your message: {data}", room=sid)
