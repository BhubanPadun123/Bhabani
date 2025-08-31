from fastapi import Query,APIRouter,Depends,HTTPException,UploadFile,File,status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.control_model import cataory_model,user_platform_model
from database import get_db
from app.platform_control.types import create_catagory_type,create_user_platform_type
from utils.cloudinary import cloudinary


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
@routes.post("/user_platform")
def create_user_platform(data: create_user_platform_type, db: Session = Depends(get_db)):
    # Check if platform already exists for this user or category
    user_platform = (
        db.query(user_platform_model)
        .filter(
            user_platform_model.catagory_ref == data.catagory_ref,
            user_platform_model.user_ref == data.user_ref
        )
        .first()
    )

    if user_platform:
        return {"message": "This platform already exists in your account!"}

    # Create new platform entry
    new_platform = user_platform_model(
        user_ref=data.user_ref,
        catagory_ref=data.catagory_ref
    )
    db.add(new_platform)
    db.commit()
    db.refresh(new_platform)

    return {"message": "Category added successfully to your account!"}

@routes.get("/user_platform")
def get_user_platform(
    user_ref:int = Query(...),
    db:Session = Depends(get_db)
):
    user_platform = db.query(user_platform_model).filter(user_platform_model.user_ref == user_ref).all()

    if not user_platform:
        return []
    
    return user_platform

@routes.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read file content
        contents = await file.read()

        # Upload to cloudinary using file-like object
        upload_result = cloudinary.uploader.upload(contents)

        return {
            "url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
