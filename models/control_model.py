from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timedelta


class cataory_model(Base):
    __tablename__ = "catagory"
    id = Column(Integer,primary_key=True,index=True)
    catagory_name = Column(String(300),nullable=False)