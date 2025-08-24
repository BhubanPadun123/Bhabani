from sqlalchemy import Column,Integer,String,ForeignKey,JSON
from database import Base
from sqlalchemy.orm import relationship

class video_model(Base):
    __tablename__ = "videos"
    id = Column(Integer,primary_key=True,index=True)
    class_ref = Column(Integer,ForeignKey('classes.id'))
    subject_ref = Column(Integer)
    topic_ref = Column(Integer)
    sl_no = Column(Integer)
    video_url = Column(JSON)
    description = Column(String(500))
    thumbnailUrl = Column(String(500)) 
class video_response_model(Base):
    __tablename__ = "video_response"
    id = Column(Integer,primary_key=True,index=True)
    video_ref = Column(Integer,ForeignKey('videos.id'))
    likes = Column(Integer)
    fav = Column(Integer)
    comment = Column(String(500))
    download = Column(Integer)
