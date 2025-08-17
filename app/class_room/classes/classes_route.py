# app/class_room/classes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.class_model import class_model
from database import get_db
from utils.types import create_class_type,update_class_name_type

route = APIRouter( 
    prefix="/classes",
    tags=["classes"]
)

@route.post('/create')
def create_classes(data: create_class_type, db: Session = Depends(get_db)):
    exist_classes = db.query(class_model).filter(class_model.class_name == data.class_name).first()

    if exist_classes:
        raise HTTPException(status_code=401, detail=f"Class already exists with name {data.class_name}")
    
    new_class = class_model(class_name=data.class_name)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return {"message": f"class created successfully with name = {data.class_name}"}

@route.delete("/remove/{id}")
def delete_class(id:int,db:Session=Depends(get_db)):
    classes = db.query(class_model).filter(class_model.id == id).first()
    if not classes:
        raise HTTPException(status_code=404,detail=f"Class does not exist with id = {id}")
    db.delete(classes)
    db.commit()
    return {"message": f"Class with id = {id} deleted successfully"}

@route.get("/all")
def get_all_classes(db: Session = Depends(get_db)):
    classes = db.query(class_model).all()
    
    if not classes:
        raise HTTPException(status_code=404, detail="No classes found")

    return {"classes": classes}

@route.put("/update/{id}")
def update_class_name(data:update_class_name_type,db:Session=Depends(get_db)):
    classes = db.query(class_model).filter(class_model.id == data.id).first()

    if not classes:
        raise HTTPException(status_code=404,detail=f"Class does not exist with id = {data.id}")
    classes.class_name = data.new_name
    db.commit()
    return {"message":"Class name updated success!"}


