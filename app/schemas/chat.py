from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    listing_id: int
    sender_id: str
    receiver_id: str

class ChatMessageOut(ChatMessageBase):
    id: int
    listing_id: int
    sender_id: str
    receiver_id: str
    timestamp: datetime
    edited: bool = False
    deleted: bool = False
    message_type: str = "text"
    message_metadata: Optional[Dict[str, Any]] = None
    reply_to_id: Optional[int] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatRoomOut(BaseModel):
    id: int
    listing_id: int
    participant1_id: str
    participant2_id: str
    created_at: datetime
    last_message_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MessageReactionOut(BaseModel):
    id: int
    message_id: int
    user_id: str
    reaction: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Optional: Schemas for editing/deleting messages
class ChatMessageEdit(BaseModel):
    message_id: int
    new_content: str

class ChatMessageDelete(BaseModel):
    message_id: int