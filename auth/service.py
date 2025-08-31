from typing import Annotated
from fastapi import Depends, HTTPException, Request, Response
from starlette import status
from .models import User
from sqlalchemy.orm import Session
from .schemas import UserCreate, UserOut
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from database import get_db
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRES_AT = os.getenv("ACCESS_TOKEN_EXPIRE_TIME")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Annotated[Session, Depends(get_db)]


def check_user_exists(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

def check_user_exists_for_login(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return user


def check_all_fields(user_model : UserCreate):
    if not user_model.email or not user_model.password or not user_model.confirm_password or not user_model.gender:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Provide All fields")
    if len(user_model.password) < 8 or len(user_model.confirm_password) < 8:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passowrds must have minimum length of 8") 
    if user_model.password != user_model.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwords must match")
    
    
def create_password(password : str):
    return bcrypt_context.hash(password)

def generate_token(email : str, id : int, response : Response):
    encode = {
        "sub" : email,
        "id" : id
    }
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=int(EXPIRES_AT))
    encode.update({"exp" : expires_at})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True, 
        samesite="None", 
        # path="/",
        max_age=3600,  
        # domain="localhost" 
        # secure=True,
        # samesite="strict"
    )


def create_user(db : Session, user_model : UserCreate, response : Response):
    hashed_password = create_password(user_model.password)
    user = User(hashed_password=hashed_password, **user_model.model_dump(exclude={"password", "confirm_password"}))
    db.add(user)
    db.commit()
    db.refresh(user)
    generate_token(user.email, user.id, response)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = check_user_exists_for_login(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return user


async def get_current_user(request : Request, db : db_dependency)-> UserOut:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no token present in cookies"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        id: int = payload.get("id")

        if email is None or id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        user = db.query(User).filter(User.id == id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return UserOut.model_validate(user)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token is invalid or expired {e}"
        )
