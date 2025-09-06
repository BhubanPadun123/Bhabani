from pydantic import BaseModel,EmailStr
from typing import List
from fastapi import Query


class create_catagory_type(BaseModel):
    catagory_name:str
class create_user_platform_type(BaseModel):
    user_ref:int
    catagory_ref:int

class feedback_create_type(BaseModel):
    user_ref:int
    message:str