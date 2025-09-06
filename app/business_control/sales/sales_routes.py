from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import sales_model,sale_product_model,transection_mode
from utils.types import create_sale_type,sale_product_type,get_customer_subscription_query_type,razorpay_request_type,create_transection_type
from models.class_model import subject_model,topic_model
from models.video_model import video_model
from utils.private import RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET
from fastapi.responses import HTMLResponse
import razorpay
from datetime import datetime
from sqlalchemy import extract, func


routes = APIRouter(
    prefix="/sales",
    tags=["sales"]
)

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@routes.post("/payment")
def request_payment(order:razorpay_request_type):
    try:
        order_data = {
            "amount": order.amount,  # amount in paise (₹500)
            "currency": order.currency,
            "payment_capture": 1,
        }
        payment = razorpay_client.order.create(data=order_data)
        return {"order": payment, "key_id": RAZORPAY_KEY_ID}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@routes.post("/create")
def create_new_sale(data:create_sale_type,db:Session = Depends(get_db)):
    new_sale = sales_model(customer_ref=data.customer_ref)

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    return {"sale_id": new_sale.id}

@routes.post('/product')
def sale_products(data:sale_product_type,db:Session = Depends(get_db)):
    sale_ref = db.query(sales_model).filter(sales_model.id == data.sale_id).first()

    if not sale_ref:
        raise HTTPException(status_code=401,detail=f"sale reference is not found")
    
    new_product_sale = sale_product_model(sale_id=data.sale_id,class_ref=data.class_ref,subject_ref=data.subject_ref)
    
    db.add(new_product_sale)
    db.commit()
    db.refresh(new_product_sale)
    
    return {"message":"course is successfully added"}

@routes.get("/subscription/{customer_ref}")
def get_customer_product(customer_ref:int,db:Session=Depends(get_db)):
    result = db.query(
        sales_model,sale_product_model,subject_model
        ).join(
            sale_product_model,sale_product_model.sale_id == sales_model.id
            ).join(subject_model,subject_model.id == sale_product_model.subject_ref).filter(
                sales_model.customer_ref == customer_ref
                ).all()
    
    if not result:
        return []
    
    final_list = []
    for sale,product,subject in result:
        final_list.append({
            "sale": sale.__dict__,
            "subject":subject.__dict__
        })
    for item in final_list:
        for part in item.values():
            part.pop("_sa_instance_state", None)
    
    return final_list
@routes.get("/videos")
def get_course_videos(
    class_ref:int = Query(...),
    subject_ref:int = Query(...),
    db:Session = Depends(get_db)
):
    videos = db.query(
        topic_model,video_model).join(
            video_model,video_model.topic_ref == topic_model.id).filter(
                video_model.class_ref == class_ref,video_model.subject_ref == subject_ref).all()

    if not videos:
        raise HTTPException(status_code=404,detail=f"Course Video not found!")
    final_list = []
    for topic,video in videos:
        final_list.append({
            "topic":topic.__dict__,
            "video":video.__dict__
        })
    
    for item in final_list:
        for part in item.values():
            part.pop("_sa_instance_state", None)
    
    return final_list

@routes.post("/transections")
def create_transection(data:create_transection_type,db:Session=Depends(get_db)):
    new_transection = transection_mode(transection_id=data.transection_id,customer_ref=data.customer_ref,amount=data.amount,date=data.date)
    db.add(new_transection)
    db.commit()
    db.refresh(new_transection)

    return {"message":"payment record's updated!"}

@routes.get("/earning/monthly_group")
def get_monthly_earnings(db: Session = Depends(get_db)):
    # Group earnings by Year + Month
    results = (
        db.query(
            extract("year", transection_mode.date).label("year"),
            extract("month", transection_mode.date).label("month"),
            func.sum(transection_mode.amount).label("total_amount"),
            func.count(transection_mode.id).label("total_transactions")
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    if not results:
        return {"message": "No transactions found"}

    # Format response month-wise
    monthly_data = []
    for row in results:
        month_name = datetime(int(row.year), int(row.month), 1).strftime("%B %Y")
        monthly_data.append({
            "month": month_name,
            "year": int(row.year),
            "month_number": int(row.month),
            "total_amount": float(row.total_amount),
            "total_transactions": int(row.total_transactions)
        })

    return {"monthly_earnings": monthly_data}

@routes.get("/transactions/monthly")
def get_all_transactions_monthly(
    year: int = Query(..., description="Year in YYYY format"),
    db: Session = Depends(get_db)
):
    transactions = (
        db.query(transection_mode)
        .filter(extract("year", transection_mode.date) == year)
        .order_by(transection_mode.date.asc())
        .all()
    )

    if not transactions:
        return {"message": f"No transactions found for {year}"}

    monthly_data = {}
    for t in transactions:
        month = t.date.month
        month_key = f"{datetime(year, month, 1).strftime('%B %Y')}"

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "year": year,
                "month_number": month,
                "transactions": []
            }

        monthly_data[month_key]["transactions"].append({
            "id": t.id,
            "transection_id": t.transection_id,
            "customer_ref": t.customer_ref,
            "amount": float(t.amount),
            "date": t.date.strftime("%Y-%m-%d %H:%M:%S")
        })

    result = [{"month": k, **v} for k, v in monthly_data.items()]

    return {"year": year, "monthly_transactions": result}

@routes.get("/user/subscription")
def check_user_subscription(
    user_ref:int = Query(...),
    db:Session = Depends(get_db)
):
    transection = db.query(transection_mode).filter(transection_mode.customer_ref == user_ref).first()

    if not transection:
        return False
    expire_date = transection.date
    
    if datetime.utcnow() > expire_date:
        return {
            "subscribed": False,
            "expired": True,
            "expire_date": expire_date,
            "last_payment_date": transection.date
        }
    return {
        "subscribed": True,
        "expired": False,
        "expire_date": expire_date,
        "last_payment_date": transection.date
    }

