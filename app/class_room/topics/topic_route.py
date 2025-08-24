from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from models.class_model import subject_model,class_model,topic_model
from database import get_db
from utils.types import create_topic_type,update_topic_type
from typing import List,Dict,Any


route = APIRouter(
    prefix="/topics",
    tags=["topics"]
)

@route.post("/create")
def create_topics(data: create_topic_type, db: Session = Depends(get_db)):
    # 1️⃣ Check if the subject exists first
    subject = db.query(subject_model).filter(subject_model.id == data.subject_ref).first()
    if not subject:
        raise HTTPException(
            status_code=404,
            detail=f"Subject with ID {data.subject_ref} not found."
        )

    # 2️⃣ Check if the topic name already exists for this subject
    topic = db.query(topic_model).filter(
        topic_model.topic_name == data.topic_name,
        topic_model.subject_ref == data.subject_ref
    ).first()
    if topic:
        raise HTTPException(
            status_code=400,
            detail=f"Topic '{data.topic_name}' already exists for this subject."
        )
    
    # 3️⃣ Create new topic
    new_topic = topic_model(subject_ref=data.subject_ref, topic_name=data.topic_name,thumbnail_url=data.thumbnail_url)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    return {"message": "Topic created successfully!"}


@route.put("/update")
def update_topic(data:update_topic_type,db:Session=Depends(get_db)):
    class_check = db.query(class_model).filter(class_model.id == data.class_ref)

    if not class_check:
        raise HTTPException(status_code=400,detail=f"Class is not available for delete the topic")
    
    topic = db.query(topic_model).filter(topic_model.id == data.topic_id,topic_model.subject_ref == data.subject_ref).first()

    if not topic:
        raise HTTPException(status_code=500,detail=f"Toopic not found!")
    
    topic.topic_name = data.new_name
    db.commit()

    return {"message":"Topic name updated successfull!"}

@route.delete("/remove/{topic_id}")
def delete_topic(topic_id:int,db:Session=Depends(get_db)):
    topic = db.query(topic_model).filter(topic_model.id == topic_id).first()

    if not topic:
        raise HTTPException(status_code=404,detail=f"topic not found!")
    
    db.delete(topic)
    db.commit()

    return {"message":"successfully deleted the topic"}
@route.get("/all/{subject_id}")
def get_all_topic(subject_id:int,db:Session=Depends(get_db)):
    results = (
        db.query(topic_model)
        .join(subject_model, subject_model.id == topic_model.subject_ref)
        .filter(subject_model.id == subject_id)
        .all()
    )
    if not results:
        return []
    return results
    
@route.get("/subject/topics")
def get_all_subject_topics(
    subjectIds: List[int] = Query(...), 
    db: Session = Depends(get_db)
) -> Dict[int, List[Dict[str, Any]]]:
    
    result: Dict[int, List[Dict[str, Any]]] = {}

    for subject_id in subjectIds:
        topics = (
            db.query(topic_model)
            .join(subject_model, topic_model.subject_ref == subject_model.id)
            .filter(topic_model.subject_ref == subject_id)
            .all()
        )
        # Convert SQLAlchemy objects to dicts
        result[subject_id] = [
            {col.name: getattr(topic, col.name) for col in topic.__table__.columns}
            for topic in topics
        ]

    return result
    

