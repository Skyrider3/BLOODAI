from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ExcelFile(Base):
    __tablename__ = "excel_files"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    file_name = Column(String, index=True)
    file_data = Column(String)
    user_id = Column(Integer, ForeignKey("users.id")) 
    user = relationship("UserModel", back_populates="files")

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)
    files = relationship("ExcelFile", back_populates="user")
