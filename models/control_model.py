from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class cataory_model(Base):
    __tablename__ = "catagory"
    id = Column(Integer, primary_key=True, index=True)
    catagory_name = Column(String(300), nullable=False)

    # Relationship to user_platform_model
    user_platforms = relationship(
        "user_platform_model",
        back_populates="category",
        cascade="all, delete"
    )


class user_platform_model(Base):
    __tablename__ = "user_platform"
    id = Column(Integer, primary_key=True, index=True)
    user_ref = Column(Integer)
    catagory_ref = Column(Integer, ForeignKey("catagory.id", ondelete="CASCADE"))

    # Relationship back to cataory_model
    category = relationship(
        "cataory_model",
        back_populates="user_platforms"
    )
