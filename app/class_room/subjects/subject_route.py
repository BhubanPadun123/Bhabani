from fastapi import APIRouter, Depends, HTTPException,File,UploadFile,Form
from sqlalchemy.orm import Session
from models.class_model import subject_model,class_model,syllabus_model
from database import get_db
from utils.types import create_subject_type,edit_subject_type,import_syllabus_type
from fastapi.responses import StreamingResponse
import pandas as pd
from io import BytesIO

route = APIRouter(
    prefix="/subjects",
    tags=["subjects"]
)


@route.post("/create")
def create_subject(data: create_subject_type, db: Session = Depends(get_db)):
    # Use the session instance `db` instead of the Session class
    query = db.query(
        class_model.id,
        class_model.class_name,
        subject_model.id,
        subject_model.subject_name,
        subject_model.subject_price
    ).join(subject_model, class_model.id == subject_model.class_ref)

    results = query.all()

    if not results:
        new_subject = subject_model(
            class_ref=data.class_ref,
            subject_name=data.subject_name,
            subject_price=data.subject_price
        )
        db.add(new_subject)  # <-- also missing before
        db.commit()
        db.refresh(new_subject)
        return {"message": "Subject created success!"}
    else:
        for items in results:
            if items[0] and items[3] and items[3] == data.subject_name and items[0] == data.class_ref:
                raise HTTPException(status_code=400,detail=f"Subject alrady exist in this class!")
            
        new_subject = subject_model(
            class_ref=data.class_ref,
            subject_name=data.subject_name,
            subject_price=data.subject_price
        )
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        return {"message": "Subject created success!"}


@route.get("/all/{class_ref}")
def get_all_class_subjects(class_ref:int,db:Session=Depends(get_db)):
    is_class_exist = db.query(class_model).filter(class_model.id == class_ref).first()

    if not is_class_exist:
        raise HTTPException(status_code=404,detail=f"Class does not exist with this reference id = {class_ref}")
    all_class_subjects = db.query(subject_model).filter(subject_model.class_ref == class_ref).all()

    if not all_class_subjects:
        raise HTTPException(status_code=401,detail=f"Subject data not found!")
    return {"list":all_class_subjects}

@route.put("/update/{subject_id}/{new_name}")
def update_subject_name(data:edit_subject_type,db:Session=Depends(get_db)):
    is_subject_exist = db.query(subject_model).filter(subject_model.id == data.id).first()

    if not is_subject_exist:
        raise HTTPException(status_code=404,detail=f"Subject does not exist with id = {data.id}")
    is_subject_exist.subject_name = data.subject_name
    is_subject_exist.class_ref = data.class_ref
    is_subject_exist.subject_price = data.subject_price
    db.commit()
    return {"message":f"Subject name updated successfull!"}

@route.delete("/remove/{id}/{class_ref}")
def delete_subject(id:int,db:Session=Depends(get_db)):
    subject = db.query(subject_model).filter(
        subject_model.id == id
        ).first()

    if not subject:
        raise HTTPException(status_code=400,detail=f"Subject does not exist with id = {id}")
    
    db.delete(subject)
    db.commit()

    return {"message":f"Subject deleted successfull!"}

@route.get("/download_template")
def donwload_syllabus_import_template():
    # Define only headers
    headers = ["lession_name", "topic_name"]
    
    #create empty col with header
    df = pd.DataFrame(columns=headers)

    file_stream = BytesIO()
    df.to_excel(file_stream,index=False)

    file_stream.seek(0)
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=syllabus_import_template.xlsx"}
    )



@route.post("/import")
def import_syllabus(
    subject_ref: int = Form(...),
    class_ref:int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    subject = (
        db.query(class_model, subject_model)
        .join(subject_model, subject_model.class_ref == class_model.id)
        .filter(subject_model.id == subject_ref)
        .first()
    )
    if not subject:
        raise HTTPException(status_code=402, detail=f"Subject does not exist with id {subject_ref}")

    # Read Excel
    try:
        contents = file.file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel: {str(e)}")

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Validate headers
    required_cols = {"lession_name", "topic_name"}
    if not required_cols.issubset(set(df.columns)):
        return {
            "message": "Template not accepted. Please use the correct Excel format.",
            "expected_columns": list(required_cols),
            "found_columns": list(df.columns)
        }

    # Create DB objects
    syllabus_records = []
    for _, row in df.iterrows():
        lession_name = str(row["lession_name"]).strip()
        topic_str = str(row["topic_name"]).strip()

        if not lession_name or not topic_str:
            continue

        topic_list = [t.strip() for t in topic_str.split(",") if t.strip()]

        syllabus_records.append(
            syllabus_model(
                subject_ref=subject_ref,
                lession_name=lession_name,
                topic_name=topic_list
            )
        )

    if not syllabus_records:
        return {"message": "Template not accepted. No valid rows found in Excel."}

    db.add_all(syllabus_records)
    db.commit()

    return {"message": f"Imported {len(syllabus_records)} syllabus records successfully"}

    