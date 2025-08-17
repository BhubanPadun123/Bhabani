from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timedelta


class user_model(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    user_name = Column(String(225))
    email = Column(String(225),unique=True,index=True)
    hashed_password = Column(String(225))
    user_type = Column(String(225))
    sales = relationship("sales_model", back_populates="customer")
class sales_model(Base):
    __tablename__ = "sales"
    id = Column(Integer,primary_key=True,index=True)
    customer_ref = Column(Integer,ForeignKey("users.id"),nullable=False)
    customer = relationship("user_model", back_populates="sales")
    products = relationship("sale_product_model", back_populates="sale")
    
class sale_product_model(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"))
    class_ref = Column(Integer, ForeignKey('classes.id', ondelete="CASCADE"))
    subject_ref = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"))
    expire_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=365))

    sale = relationship("sales_model", back_populates="products")

class transection_mode(Base):
    __tablename__ = "transection"
    id = Column(Integer,primary_key=True,index=True)
    transection_id = Column(String(300),nullable=False)
    customer_ref = Column(Integer)
    amount = Column(Integer,nullable=False)
    date = Column(DateTime, default=datetime.utcnow())
