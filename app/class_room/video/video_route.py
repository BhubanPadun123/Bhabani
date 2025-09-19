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
from azure.storage.blob import BlobServiceClient,generate_blob_sas,BlobSasPermissions
import os
import json
from datetime import datetime,timedelta
from urllib.parse import quote




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
account_key = os.getenv("AZURE_STORAGE_KEY")

CHUNK_SIZE = 4 * 1024 * 1024
def is_azure_connected()-> bool:
    try:
        blob_service_client.get_service_properties()
        return True
    except Exception as e:
        print(f"Error while connect the azure {e}")
        return False
def get_blob_sas_url(blob_name:str)-> str :
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=365)
    )
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}?{sas_token}"

@route.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Save file locally first
        local_file_path = f"/tmp/{file.filename}"
        with open(local_file_path, "wb") as f:
            f.write(await file.read())

        file_size = os.path.getsize(local_file_path)

        # Case 1: Small file -> Cloudinary
        if file_size <= 100 * 1024 * 1024:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                local_file_path,
                resource_type="video",
                public_id=str(uuid.uuid4())
            )
            os.remove(local_file_path)
            return {"provider": "cloudinary", "urls": [result.get("secure_url")]}

        # Case 2: Large file -> Azure Block Blob with chunking
        else:
            blob_name = f"{uuid.uuid4()}_{file.filename}"
            blob_client = container_client.get_blob_client(blob_name)

            # Stage blocks in chunks
            block_ids = []
            with open(local_file_path, "rb") as f:
                index = 0
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    block_id = str(index).zfill(6)  # must be base64, see note below
                    blob_client.stage_block(
                        block_id=block_id,
                        data=chunk
                    )
                    block_ids.append(block_id)
                    index += 1

            # Commit blocks
            blob_client.commit_block_list(block_ids)

            os.remove(local_file_path)
            return {"provider": "azure", "urls": [blob_name]}

    except Exception as e:
        os.remove(local_file_path)
        print(e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@route.get("/video/{blob_name:path}")
def get_video_url(blob_name: str):
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,  # use raw name
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=2)
    )
    # URL-encode blob_name for safety in browsers
    encoded_blob_name = quote(blob_name, safe="/")
    url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{encoded_blob_name}?{sas_token}"
    return {"url": url}
            
@route.post("/create")
def create_video(data:video_create_type,db:Session = Depends(get_db)):
    # check_exists = db.query(
    #     class_model,subject_model,topic_model
    #     ).join(
    #         subject_model,subject_model.class_ref == class_model.id
    #         ).join(
    #             topic_model,topic_model.subject_ref == subject_model.id
    #             ).filter(
    #                 class_model.id == data.class_ref,
    #                 subject_model.id == data.subject_ref,
    #                 topic_model.id == data.topic_ref
    #             ).first()
    # if not check_exists:
    #     raise HTTPException(status_code=500,detail=f"Privides data are not matching with any of the row")
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
    