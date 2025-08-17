from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import user_model
from utils import types
from utils.private import verify_token

routes = APIRouter(
    prefix="/monitor",
    tags=["monitor"]
)

@routes.get("/all")
def user_list(db:Session=Depends(get_db),token_data:dict=Depends(verify_token)):
    users = db.query(user_model).all()

    if not users:
        raise HTTPException(status_code=404,detail=f"User does not exist!")
    
    return {
        "user_list":users
    }
@routes.put('/update_role')
def user_user_role(data:types.update_user_role_type,db:Session=Depends(get_db),token_data:dict=Depends(verify_token)):
    user = db.query(user_model).filter(user_model.id == data.user_id).first()

    if not user:
        raise HTTPException(401,detail=f"user does not exist with id = {data.user_id}")
    user.user_type = data.new_user_type
    db.commit()
    return {
        "message":"user type updated successfully!"
    }