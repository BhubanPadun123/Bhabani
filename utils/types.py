from pydantic import BaseModel,EmailStr
from typing import List
from fastapi import Query


class create_user(BaseModel):
    id:str
    user_name:str
    email:EmailStr
    hashed_password:str
    user_type:str
    org_id:str
class reset_password_type(BaseModel):
    email:EmailStr
    new_password:str
class update_user_role_type(BaseModel):
    user_id:str
    new_user_type:str

class create_class_type(BaseModel):
    class_name:str
class update_class_name_type(BaseModel):
    id:int
    new_name:str
class create_subject_type(BaseModel):
    class_ref:int
    subject_name:str
    subject_price:int
class create_topic_type(BaseModel):
    subject_ref:int
    topic_name:str
class update_topic_type(BaseModel):
    subject_ref:int
    class_ref:int
    topic_id:int
    new_name:str
class edit_subject_type(BaseModel):
    id:int
    class_ref:int
    subject_name:str
    subject_price:int
class import_syllabus_type(BaseModel):
    subject_ref:int

class video_create_type(BaseModel):
    class_ref:int
    subject_ref:int
    topic_ref:int
    sl_no:int
    video_url:List[str]
    description:str

class subject_video_query_type(BaseModel):
    class_ref:int = Query(...)
    subject_ref:int = Query(...)

class create_sale_type(BaseModel):
    customer_ref:int

class sale_product_type(BaseModel):
    sale_id:int
    class_ref:int
    subject_ref:int
class get_customer_subscription_query_type(BaseModel):
    customer_ref:int
class add_topic_video_type(BaseModel):
    class_ref:int
    subject_ref:int
    topic_ref:int
    video_url:List[str]

class razorpay_request_type(BaseModel):
    amount:int
    currency: str = "INR"
    receipt: str

class create_transection_type(BaseModel):
    transection_id:str
    customer_ref:int
    amount:int