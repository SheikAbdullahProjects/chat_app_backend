from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import Base, engine
from auth.routes import router as a_router
from conversation.routes import router as c_router
from chat_socket import sio   # <-- import socketio server
import socketio

load_dotenv()

# --- FastAPI setup ---
app = FastAPI(
    title="Chat Application",
    description="Chat Application with Images sending functionality",
    version="0.1"
)

# CORS middleware for REST API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat-app-frontend-ecfx.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(a_router)
app.include_router(c_router)

@app.get("/")
async def get_root():
    return {"detail": "Working Fine"}

# --- Combine FastAPI app with Socket.IO ---
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

app = socket_app
