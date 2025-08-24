from sqlalchemy import Column,Integer,String,ForeignKey,JSON
from database import Base
from sqlalchemy.orm import relationship


class class_model(Base):
    __tablename__ = "classes"
    id = Column(Integer,primary_key=True,index=True)
    class_name = Column(String(300),unique=True,nullable=False)
    category = Column(String(300),default="academic",nullable=False)
    subjects = relationship(
        "subject_model",
        back_populates="class_",
        cascade="all, delete"
    )

class subject_model(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    class_ref = Column(Integer, ForeignKey('classes.id',ondelete="CASCADE",onupdate="CASCADE"))
    subject_name = Column(String(500))
    subject_price = Column(Integer)
    sub_catagory = Column(String(500))

    class_ = relationship("class_model", back_populates="subjects")
    topics = relationship("topic_model", back_populates="subject", cascade="all, delete-orphan", passive_deletes=True)
    products = relationship("sale_product_model", cascade="all, delete-orphan", passive_deletes=True)
class syllabus_model(Base):
    __tablename__ = "syllabus"
    id = Column(Integer,primary_key=True,index=True)
    subject_ref = Column(Integer,ForeignKey('subjects.id',ondelete="CASCADE",onupdate="CASCADE"))
    lession_name = Column(String(500))
    topic_name = Column(JSON)


class topic_model(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_ref = Column(Integer, ForeignKey('subjects.id',ondelete="CASCADE",onupdate="CASCADE"))
    topic_name = Column(String(500))
    thumbnail_url = Column(String(500))

    subject = relationship("subject_model", back_populates="topics")


