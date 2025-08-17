from fastapi import Query,APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from models.control_model import cataory_model
from database import get_db
from app.platform_control.types import create_catagory_type


routes = APIRouter(
    prefix="/platform",
    tags=["platform"]
)

@routes.post("/create")
def create_catagory(data:create_catagory_type,db:Session = Depends(get_db)):
    catarogy = db.query(cataory_model).filter(cataory_model.catagory_name == data.catagory_name).first()

    if catarogy:
        return {"message":"Catagory already exist!"}
    
    new_catagory = cataory_model(catagory_name=data.catagory_name)
    db.add(new_catagory)
    db.commit()
    db.refresh(new_catagory)

    return {"message":"catagory created success!"}

@routes.get("/catogory")
def get_all_catagory(db:Session=Depends(get_db)):
    catagores = db.query(cataory_model).all()

    if not catagores:
        return []
    return catagores