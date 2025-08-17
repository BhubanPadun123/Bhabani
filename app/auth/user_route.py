from fastapi import APIRouter,Depends,HTTPException,Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models.user_model import user_model
from database import get_db
from utils import hashing
from utils.types import create_user,reset_password_type
from utils.private import create_access_token
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from utils.private import GOOGLE_KEY
from jose import jwt


google_config = Config(environ={
    "GOOGLE_CLIENT_ID": "95479022789-o68lrqcufddqbc2r504mirdavfl1fkji.apps.googleusercontent.com",
    "GOOGLE_CLIENT_SECRET": "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    ",
    "SECRET_KEY": GOOGLE_KEY
})

oauth = OAuth(google_config)
oauth.register(
    name="google",
    client_id=google_config("GOOGLE_CLIENT_ID"),
    client_secret=google_config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
ALGORITHM = "HS256"

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")

    email = user_info["email"]
    name = user_info.get("name")
    picture = user_info.get("picture")

    # check if user exists
    user = db.query(user_model).filter(user_model.email == email).first()
    if not user:
        # create new user
        user = user_model(email=email, full_name=name, picture=picture, provider="google")
        db.add(user)
        db.commit()
        db.refresh(user)

    # issue JWT for frontend
    jwt_token = jwt.encode({"sub": str(user.id), "email": user.email}, GOOGLE_KEY, algorithm=ALGORITHM)

    # redirect to frontend with token (e.g. query param)
    return RedirectResponse(f"http://localhost:3000?token={jwt_token}")
@router.post('/register')
def user_create(user_data:create_user,db:Session = Depends(get_db)):
    #Check if email already exist
    exist_email = db.query(user_model).filter(user_model.email == user_data.email).first()
    if exist_email:
        raise HTTPException(status_code=400,detail="Email already registered")
    
    hashed_password = hashing.hash_password(user_data.hashed_password)
    user = user_model(user_name=user_data.user_name,email=user_data.email,hashed_password=hashed_password,user_type=user_data.user_type)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
@router.get("/login/{email}/{password}")
def user_login(email:str,password:str,db:Session=Depends(get_db)):
    user = db.query(user_model).filter(user_model.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    if not hashing.verify_password(password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Incorrect Password!")
    token_data = {"sub":user.email,"user_id":user.id}
    access_token = create_access_token(token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "user_name": user.user_name,
            "email": user.email,
            "user_type": user.user_type
        }
    }
@router.put('/reset_password')
def user_reset_password(data:reset_password_type,db:Session=Depends(get_db)):
    user = db.query(user_model).filter(user_model.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401,detail=f"user does not exist with email = {data.email}")
    hash_password = hashing.hash_password(data.new_password)
    user.hashed_password = hash_password

    db.commit()
    return {"message": "Password reset successful"}


    
    