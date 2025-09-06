from fastapi import APIRouter,HTTPException,UploadFile,File,Depends,Query
from database import get_db
from models.video_model import video_model,video_response_model
from models.class_model import class_model,topic_model,subject_model
from utils.private import SECRET_KEY,SUPABASE_URL
from supabase import create_client,Client
from sqlalchemy.orm import Session
import tempfile,shutil,os,subprocess
from utils.cloudinary import cloudinary
from typing import List,Dict,Any
import uuid
import math
import json
from utils.types import video_create_type,subject_video_query_type,add_topic_video_type
from azure.storage.blob import BlobServiceClient
import os
import json




supabase:Client = create_client(SUPABASE_URL,SECRET_KEY)
route = APIRouter(
    prefix="/video",
    tags=["video"]
)
MAX_MB = 1500  # 1.5 GB
MAX_BYTES = MAX_MB * 1024 * 1024  

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)


@route.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        file_size = os.path.getsize(temp_file_path)

        # ✅ Case 1: If file <= 100MB → Cloudinary
        if file_size <= 100 * 1024 * 1024:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                temp_file_path,
                resource_type="video",
                public_id=f"{uuid.uuid4()}"
            )
            os.remove(temp_file_path)
            return {"provider": "cloudinary", "urls": [result.get("secure_url")]}

        # ✅ Case 2: If file > 100MB → Azure (chunk upload for up to 1.5 GB)
        else:
            blob_name = f"{uuid.uuid4()}_{file.filename}"
            blob_client = container_client.get_blob_client(blob_name)

            # Upload in chunks
            with open(temp_file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    blob_type="BlockBlob",
                    max_concurrency=4,  # parallel uploads
                    length=file_size,
                )

            os.remove(temp_file_path)
            return {
                "provider": "azure",
                "urls": [blob_client.url]
            }

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
            
@route.post("/create")
def create_video(data:video_create_type,db:Session = Depends(get_db)):
    check_exists = db.query(
        class_model,subject_model,topic_model
        ).join(
            subject_model,subject_model.class_ref == class_model.id
            ).join(
                topic_model,topic_model.subject_ref == subject_model.id
                ).filter(
                    class_model.id == data.class_ref,
                    subject_model.id == data.subject_ref,
                    topic_model.id == data.topic_ref
                ).first()
    if not check_exists:
        raise HTTPException(status_code=500,detail=f"Privides data are not matching with any of the row")
    new_video = video_model(
        class_ref=data.class_ref,
        subject_ref=data.subject_ref,
        topic_ref=data.topic_ref,
        sl_no = data.sl_no,
        video_url = data.video_url,
        description = data.description,
        thumbnailUrl = data.thumbnailUrl
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return {"message":"Video created successfull!"}

@route.get("/all")
def get_all_subject_video(
    class_ref: int = Query(...),
    subject_ref: int = Query(...),
    db: Session = Depends(get_db)
):
    videos = (
        db.query(class_model, subject_model, video_model)
        .join(subject_model, subject_model.class_ref == class_model.id)
        .join(video_model, video_model.subject_ref == subject_model.id)
        .filter(
            class_model.id == class_ref,
            subject_model.id == subject_ref
        )
        .all()
    )

    if not videos:
        return {"videos": []}

    # Convert to list of dicts
    result = []
    for cls, subj, vid in videos:
        result.append({
            "class": cls.__dict__,
            "subject": subj.__dict__,
            "video": vid.__dict__
        })

    # Remove SQLAlchemy internals
    for item in result:
        for part in item.values():
            part.pop("_sa_instance_state", None)

    return {"videos": result}
@route.get("/topics_videos")
def get_subject_topic_videos(
    subject_ref:int=Query(...),
    topic_ref:int=Query(...),
    db:Session=Depends(get_db)
):
    videos = db.query(video_model).filter(video_model.subject_ref == subject_ref,video_model.id == topic_ref).all()

    if not videos:
        return []
    return videos
@route.put("/add_topic_video")
def add_video_in_topic(data:add_topic_video_type,db:Session=Depends(get_db)):
    video = db.query(video_model).filter(video_model.class_ref == data.class_ref,video_model.subject_ref == data.subject_ref,video_model.id == data.topic_ref).first()

    if not video:
        raise HTTPException(status_code=204,detail=f"video does not exist with provided data!")
    video.video_url = data.video_url
    db.commit()
    return {"message":"Video added to the same topic"}

@route.get("/initial_videos")
def get_initial_videos(
    ids: List[int] = Query(...),
    db: Session = Depends(get_db)
) -> Dict[int, List[Any]]:
    result: Dict[int, List[Any]] = {}

    for class_id in ids:
        videos = (
            db.query(topic_model)
            .join(subject_model, subject_model.id == topic_model.subject_ref)
            .join(class_model, class_model.id == subject_model.class_ref)
            .filter(class_model.id == class_id)
            .order_by(topic_model.id.desc())   # recent first
            .limit(10)
            .all()
        )

        result[class_id] = [
            {
                "id": v.id,
                "class_ref": v.subject.class_ref if v.subject else None,
                "subject_ref": v.subject_ref,
                "topic_ref": v.id,
                "thumbnailUrl": v.thumbnail_url,
                "name": v.topic_name,
            }
            for v in videos
        ]

    return result

@route.get("/topic/video")
def get_topic_video(
    class_ref:int = Query(...),
    subject_ref:int = Query(...),
    topic_ref:int = Query(...),
    db:Session = Depends(get_db)
):
    video = db.query(video_model).filter(video_model.class_ref == class_ref,video_model.subject_ref == subject_ref,video_model.topic_ref == topic_ref).all()

    if not video:
        return {"message":"Video does not exist"}
    return video
    