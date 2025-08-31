from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from starlette import status
from .models import User
from .schemas import UserCreate, UserOut, UserLogin
from typing import Annotated, List
from sqlalchemy.orm import Session
from database import get_db
from .service import authenticate_user, check_user_exists, check_all_fields, create_user as create_user_srv, generate_token, get_current_user
from cloudinary_srv import delete_file, upload_file

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(db : db_dependency, user_model : UserCreate, response : Response):
    try:
        check_user_exists(db, user_model.email)
        check_all_fields(user_model)
        user = create_user_srv(db, user_model, response)
        return user
    except HTTPException as http_exp:
        raise http_exp
    except Exception as exp:
        print(exp)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exp)
        )
    
@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserOut)
async def login_user(db: db_dependency, user_model : UserLogin, response : Response):
    try:
        user = authenticate_user(db, user_model.email, user_model.password)
        generate_token(user.email, user.id, response)
        return user
    except HTTPException as http_exp:
        raise http_exp
    except Exception as exp:
        print(exp)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exp)
        )
    
    
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(response : Response):
    try:
        response.set_cookie(
            key="access_token",
            value="",
            max_age=0
        )
        return {
            "status" : status.HTTP_200_OK,
            "detail" : "Logout Successfully"
        }
    except HTTPException as http_exp:
        raise http_exp
    except Exception as exp:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exp)
        )
        
@router.put("/update-profile", status_code=status.HTTP_200_OK, response_model=UserOut)
async def update_user(db : db_dependency, current_user : user_dependency, profilePic: UploadFile = File(...)):
    try:
        user = db.query(User).filter(User.email == current_user.email).first()
        if user.profile_picture is not None:
            delete_file(user.profile_public_id)
        result = upload_file(profilePic.file)
        user.profile_picture = result["secure_url"]
        user.profile_public_id = result["public_id"]
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", status_code=status.HTTP_200_OK, response_model=List[UserOut])
async def get_all_users(db : db_dependency, current_user : user_dependency):
    try:
        users = db.query(User).filter(User.id != current_user.id).all()
        return users
    except HTTPException as htp_exp:
        raise htp_exp
    except Exception as exp:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))


@router.get("/check",status_code=status.HTTP_200_OK)
async def check_auth(user:user_dependency):
    try:
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# @app.post("/upload/")
# async def upload_image(file: UploadFile = File(...)):
#     try:
#         result = upload_file(file.file)
#         return {"url": result["secure_url"], "public_id": result["public_id"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.delete("/delete/{public_id}")
# async def delete_image(public_id: str):
#     try:
#         result = delete_file(public_id)
#         return {"result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))