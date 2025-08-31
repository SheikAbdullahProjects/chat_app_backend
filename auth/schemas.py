from pydantic import BaseModel, Field, EmailStr
from .enums import Gender
from datetime import datetime


class UserBase(BaseModel):
    username : str = Field(min_length=3)
    email : EmailStr
    gender : Gender
    
class UserCreate(UserBase):
    password : str = Field(min_length=8)
    confirm_password : str = Field(min_length=8)

class UserLogin(BaseModel):
    email : EmailStr
    password : str = Field(min_length=8)

class UserOut(UserBase):
    id : int
    is_active : bool
    profile_picture : str | None = None
    created_at : datetime
    updated_at : datetime
    
    class Config:
        from_attributes = True