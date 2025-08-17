from fastapi import APIRouter,HTTPException,UploadFile,File,Depends,Query
from database import get_db
from models.video_model import video_model,video_response_model
from models.class_model import class_model,topic_model,subject_model
from utils.private import SECRET_KEY,SUPABASE_URL
from supabase import create_client,Client
from sqlalchemy.orm import Session
import tempfile,shutil,os,subprocess
from utils.cloudinary import cloudinary
from typing import List
import uuid
import math
import json
from utils.types import video_create_type,subject_video_query_type,add_topic_video_type


supabase:Client = create_client(SUPABASE_URL,SECRET_KEY)
route = APIRouter(
    prefix="/video",
    tags=["video"]
)
UPLOAD_PROGRESS = {}
MAX_MB = 99
MAX_BYTES = MAX_MB * 1024 * 1024

def get_video_bitrate(path):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=bit_rate",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    bitrate_info = json.loads(result.stdout)
    return int(bitrate_info["format"]["bit_rate"])  # bits per second

@route.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        file_size = os.path.getsize(temp_file_path)

        if file_size <= MAX_BYTES:
            result = cloudinary.uploader.upload(
                temp_file_path,
                resource_type="video",
                public_id=f"{uuid.uuid4()}"
            )
            os.remove(temp_file_path)
            return {"urls": [result.get("secure_url")]}

        # Calculate duration per part based on bitrate
        bitrate = get_video_bitrate(temp_file_path)  # bits per second
        target_seconds = math.floor((MAX_BYTES * 8) / bitrate)  # duration per 99MB

        # Split into sequential parts
        subprocess.run([
            "ffmpeg", "-i", temp_file_path, "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", str(target_seconds),
            "-reset_timestamps", "1", "part%03d.mp4"
        ], check=True)

        part_urls = []
        for fname in sorted(f for f in os.listdir(".") if f.startswith("part") and f.endswith(".mp4")):
            result = cloudinary.uploader.upload(
                fname,
                resource_type="video",
                public_id=f"{uuid.uuid4()}"
            )
            part_urls.append(result.get("secure_url"))
            os.remove(fname)

        os.remove(temp_file_path)

        return {
            "message": f"Uploaded {len(part_urls)} sequential parts",
            "urls": part_urls
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error - {e}")
    
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
        description = data.description
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
    