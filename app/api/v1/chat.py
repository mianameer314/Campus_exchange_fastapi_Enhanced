from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from starlette.websockets import WebSocketState
from jose import JWTError, jwt
from app.core.config import settings

from app.api.deps import get_db, get_current_user
from app.models.chat import ChatMessage, BlockedUser, ChatRoom, MessageReaction
from app.models.listing import Listing
from app.models.user import User
from app.schemas.chat import ChatMessageOut, ChatRoomOut, MessageReactionOut
from app.utils.storage import save_upload
from typing import Dict, List, Optional
import html
import logging
import json
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])

active_connections: Dict[str, List[WebSocket]] = {}

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

logger = logging.getLogger("chat_ws")

def room_id(listing_id: int, u1: int, u2: int):
    return f"{listing_id}-{min(u1, u2)}-{max(u1, u2)}"

def create_message(db: Session, data: dict):
    msg = ChatMessage(**data)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    # Update chat room last message timestamp
    room = db.query(ChatRoom).filter(
        ChatRoom.listing_id == data["listing_id"],
        ((ChatRoom.participant1_id == data["sender_id"]) & (ChatRoom.participant2_id == data["receiver_id"])) |
        ((ChatRoom.participant1_id == data["receiver_id"]) & (ChatRoom.participant2_id == data["sender_id"]))
    ).first()
    
    if room:
        room.last_message_at = msg.timestamp
        db.commit()
    
    return msg

def user_blocked(db: Session, user_id: str, blocked_by: str):
    return db.query(BlockedUser).filter(
        BlockedUser.user_id == user_id,
        BlockedUser.blocked_by == blocked_by
    ).first() is not None

async def get_current_user_websocket(websocket: WebSocket, db: Session):
    auth = websocket.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise Exception("Missing or invalid authorization header")
    token = auth[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise Exception("Invalid token: no subject")
        # Optionally verify user in DB
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise Exception("User not found")
        return user_id
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise Exception("Token decode error")

@router.get("/rooms", response_model=List[ChatRoomOut])
def get_user_chat_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chat rooms for the current user"""
    rooms = db.query(ChatRoom).options(
        joinedload(ChatRoom.listing),
        joinedload(ChatRoom.participant1),
        joinedload(ChatRoom.participant2)
    ).filter(
        (ChatRoom.participant1_id == current_user.id) | 
        (ChatRoom.participant2_id == current_user.id)
    ).order_by(ChatRoom.last_message_at.desc().nullslast()).all()
    
    return rooms

@router.get("/rooms/{room_id}/messages")
def get_chat_messages(
    room_id: int,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages for a specific chat room"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if current_user.id not in [room.participant1_id, room.participant2_id]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = db.query(ChatMessage).options(
        joinedload(ChatMessage.sender),
        joinedload(ChatMessage.reply_to)
    ).filter(
        ChatMessage.listing_id == room.listing_id,
        ((ChatMessage.sender_id == room.participant1_id) & (ChatMessage.receiver_id == room.participant2_id)) |
        ((ChatMessage.sender_id == room.participant2_id) & (ChatMessage.receiver_id == room.participant1_id)),
        ChatMessage.deleted == False
    ).order_by(ChatMessage.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Mark messages as read
    unread_messages = db.query(ChatMessage).filter(
        ChatMessage.listing_id == room.listing_id,
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.read_at.is_(None)
    ).all()
    
    for msg in unread_messages:
        msg.read_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "messages": [msg.to_dict() if hasattr(msg, 'to_dict') else ChatMessageOut.from_orm(msg).dict() for msg in reversed(messages)],
        "page": page,
        "page_size": page_size,
        "total": len(messages)
    }

@router.post("/rooms/{room_id}/messages/file")
async def upload_file_message(
    room_id: int,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file as a chat message"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if current_user.id not in [room.participant1_id, room.participant2_id]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Save file
    file_url = save_upload(file, subdir="chat")
    
    # Determine message type
    message_type = "file"
    if file.content_type and file.content_type.startswith("image/"):
        message_type = "image"
    
    # Create message
    other_participant = room.participant2_id if current_user.id == room.participant1_id else room.participant1_id
    
    message_data = {
        "listing_id": room.listing_id,
        "sender_id": current_user.id,
        "receiver_id": other_participant,
        "content": caption or f"Shared a {message_type}",
        "message_type": message_type,
        "metadata": {
            "file_url": file_url,
            "file_name": file.filename,
            "file_size": file.size,
            "content_type": file.content_type
        }
    }
    
    message = create_message(db, message_data)
    return ChatMessageOut.from_orm(message)

@router.post("/messages/{message_id}/reactions")
def add_reaction(
    message_id: int,
    reaction: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a reaction to a message"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check if user is part of the conversation
    if current_user.id not in [message.sender_id, message.receiver_id]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if reaction already exists
    existing_reaction = db.query(MessageReaction).filter(
        MessageReaction.message_id == message_id,
        MessageReaction.user_id == current_user.id,
        MessageReaction.reaction == reaction
    ).first()
    
    if existing_reaction:
        # Remove reaction if it exists
        db.delete(existing_reaction)
        db.commit()
        return {"message": "Reaction removed"}
    else:
        # Add new reaction
        new_reaction = MessageReaction(
            message_id=message_id,
            user_id=current_user.id,
            reaction=reaction
        )
        db.add(new_reaction)
        db.commit()
        
        return {"message": "Reaction added"}

@router.post("/block/{user_id}")
def block_user(
    user_id: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Block a user"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_block = db.query(BlockedUser).filter(
        BlockedUser.user_id == user_id,
        BlockedUser.blocked_by == current_user.id
    ).first()
    
    if existing_block:
        raise HTTPException(status_code=400, detail="User already blocked")
    
    block = BlockedUser(
        user_id=user_id,
        blocked_by=current_user.id,
        reason=reason
    )
    db.add(block)
    db.commit()
    
    return {"message": "User blocked successfully"}

@router.delete("/block/{user_id}")
def unblock_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unblock a user"""
    block = db.query(BlockedUser).filter(
        BlockedUser.user_id == user_id,
        BlockedUser.blocked_by == current_user.id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="User not blocked")
    
    db.delete(block)
    db.commit()
    
    return {"message": "User unblocked successfully"}

@router.get("/blocked")
def get_blocked_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of blocked users"""
    blocked = db.query(BlockedUser).options(
        joinedload(BlockedUser.user)
    ).filter(BlockedUser.blocked_by == current_user.id).all()
    
    return [
        {
            "user_id": block.user_id,
            "email": block.user.email,
            "blocked_at": block.created_at,
            "reason": block.reason
        }
        for block in blocked
    ]

@router.websocket("/{listing_id}/{peer_id}")
async def chat_ws(websocket: WebSocket, listing_id: int, peer_id: str, db: Session = Depends(get_db)):
    try:
        # 🔐 Authenticate the user
        try:
            user_id = await get_current_user_websocket(websocket, db)
        except Exception as e:
            logger.error(f"Auth failed: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 🏷️ Check listing
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 🚫 Check if user is blocked
        if user_blocked(db, user_id, peer_id) or user_blocked(db, peer_id, user_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 🚫 Prevent self-chat
        if peer_id == user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        is_seller = user_id == str(listing.owner_id)
        is_buyer_chatting_with_owner = peer_id == str(listing.owner_id)

        # ❌ Invalid access check
        if not (is_seller or is_buyer_chatting_with_owner):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # ✅ Accept the connection now
        await websocket.accept()

        # 💬 Create or fetch chat room
        room = db.query(ChatRoom).filter(
            ChatRoom.listing_id == listing_id,
            ((ChatRoom.participant1_id == user_id) & (ChatRoom.participant2_id == peer_id)) |
            ((ChatRoom.participant1_id == peer_id) & (ChatRoom.participant2_id == user_id))
        ).first()

        if not room:
            room = ChatRoom(
                listing_id=listing_id,
                participant1_id=min(user_id, peer_id),
                participant2_id=max(user_id, peer_id)
            )
            db.add(room)
            db.commit()

        rid = room_id(listing_id, user_id, peer_id)
        active_connections.setdefault(rid, []).append(websocket)
        logger.info(f"User {user_id} connected to room {rid}")

        while True:
            data = await websocket.receive_json()

            if "typing" in data and data["typing"]:
                for conn in active_connections.get(rid, []):
                    if conn != websocket and conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json({"typing": True, "user": user_id})

            elif "delivery_receipt" in data:
                message_id = data["delivery_receipt"]
                msg = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
                if msg and msg.receiver_id == user_id:
                    msg.read_at = datetime.utcnow()
                    db.commit()

                for conn in active_connections.get(rid, []):
                    if conn != websocket and conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json({"delivery_receipt": message_id, "user": user_id})

            elif "edit_message" in data:
                edit_data = data["edit_message"]
                msg_db = db.query(ChatMessage).filter(ChatMessage.id == edit_data["message_id"]).first()
                if msg_db and msg_db.sender_id == user_id:
                    new_text = html.escape(edit_data["new_content"].strip())
                    if new_text:
                        msg_db.content = new_text
                        msg_db.edited = True
                        db.commit()
                        msg_out = ChatMessageOut.from_orm(msg_db).dict()
                        msg_out["timestamp"] = msg_out["timestamp"].isoformat()
                        for conn in active_connections.get(rid, []):
                            if conn.application_state == WebSocketState.CONNECTED:
                                await conn.send_json({"edit_message": msg_out})

            elif "delete_message" in data:
                message_id = data["delete_message"]
                msg_db = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
                if msg_db and msg_db.sender_id == user_id:
                    msg_db.deleted = True
                    db.commit()
                    for conn in active_connections.get(rid, []):
                        if conn.application_state == WebSocketState.CONNECTED:
                            await conn.send_json({"delete_message": message_id})

            elif "reply_to" in data:
                content = html.escape(data["content"].strip())
                reply_to_id = data["reply_to"]
                if not content:
                    continue
                msg_in = {
                    "listing_id": listing_id,
                    "sender_id": user_id,
                    "receiver_id": peer_id,
                    "content": content,
                    "reply_to_id": reply_to_id
                }
                msg = create_message(db, msg_in)
                msg_out = ChatMessageOut.from_orm(msg).dict()
                msg_out["timestamp"] = msg_out["timestamp"].isoformat()
                for conn in list(active_connections.get(rid, [])):
                    if conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json(msg_out)

            elif "content" in data:
                content = html.escape(data["content"].strip())
                if not content:
                    continue
                msg_in = {
                    "listing_id": listing_id,
                    "sender_id": user_id,
                    "receiver_id": peer_id,
                    "content": content
                }
                msg = create_message(db, msg_in)
                msg_out = ChatMessageOut.from_orm(msg).dict()
                msg_out["timestamp"] = msg_out["timestamp"].isoformat()
                for conn in list(active_connections.get(rid, [])):
                    if conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json(msg_out)

            else:
                await websocket.send_json({"error": "Invalid payload."})

    except WebSocketDisconnect:
        if rid in active_connections and websocket in active_connections[rid]:
            active_connections[rid].remove(websocket)
            if not active_connections[rid]:
                del active_connections[rid]
        logger.info(f"User {user_id} disconnected from room {rid}")

    except Exception as e:
        logger.error(f"Unexpected error in websocket: {e}", exc_info=True)
        if rid in active_connections and websocket in active_connections[rid]:
            active_connections[rid].remove(websocket)
            if not active_connections[rid]:
                del active_connections[rid]
        try:
            await websocket.close()
        except RuntimeError:
            pass  # Connection already closed
