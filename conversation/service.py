from .models import Message
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import Message
from typing import Optional
from sqlalchemy import or_, and_
from chat_socket import send_new_message


async def create_message(db: Session, sender_id: int, receiver_id: int, content: Optional[str], res: Optional[dict]):
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        image_url=res.get("secure_url") if res else None,
        image_id=res.get("public_id") if res else None
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Convert message to dict for Socket.IO emission
    message_data = {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "image_url": message.image_url,
        "image_id": message.image_id,
        "created_at": message.created_at.isoformat() if message.created_at else None
    }
    
    # Send via Socket.IO
    success = await send_new_message(receiver_id, message_data)
    
    if success:
        print({"status": "success", "message": "Message sent via Socket.IO"})
    else:
        print({"status": "offline", "message": "User is offline"})
    
    return message  # Return the actual message object, NOT a coroutine

def get_messages(db : Session, sender_id, receiver_id):
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == sender_id, Message.receiver_id == receiver_id),
            and_(Message.sender_id == receiver_id, Message.receiver_id == sender_id)
        )
    ).order_by(Message.created_at.asc()).all()
    return messages