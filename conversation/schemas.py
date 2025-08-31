from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: Optional[str]
    image_url: Optional[str]
    image_id: Optional[str]
    
class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes : True