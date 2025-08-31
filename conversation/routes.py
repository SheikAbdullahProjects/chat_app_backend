from fastapi import APIRouter, Form, HTTPException, Depends, Path, UploadFile, File
from typing import List, Optional
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from database import get_db
from auth.service import get_current_user
from .schemas import MessageCreate, MessageOut
from auth.models import User
from cloudinary_srv import upload_file
from .service import create_message, get_messages

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



router = APIRouter(
    prefix="/messages",
    tags=["Message"]
)

@router.get("/{receiver_id}/", status_code=status.HTTP_200_OK, response_model=List[MessageOut])
async def get_all_messages(db : db_dependency, current_user : user_dependency, receiver_id : int = Path(ge=1)):
    try:
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        messages = get_messages(db, current_user.id, receiver.id)
        return messages
    except HTTPException as htp_err:
        raise htp_err
    except Exception as exp:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exp)
        )



@router.post("/send/{receiver_id}", status_code=status.HTTP_201_CREATED)
async def send_message(db : db_dependency, current_user : user_dependency, receiver_id : int = Path(ge=1), content: Optional[str] = Form(None),img_file: Optional[UploadFile] = File(None),):
    try:
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        if not content and not img_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message must contain either text or an image"
            )
        res = None
        if img_file:
            res = upload_file(img_file.file)

        message = await create_message(db, current_user.id, receiver.id, content, res)
        return message
    except HTTPException as htp_err:
        raise htp_err
    except Exception as exp:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exp)
        )