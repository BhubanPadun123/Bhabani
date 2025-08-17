from pydantic import BaseModel,EmailStr
from typing import List
from fastapi import Query


class create_catagory_type(BaseModel):
    catagory_name:str