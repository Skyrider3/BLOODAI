from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

DOCTORS_DATABASE_URL = "sqlite:///./doctors.db"
doctors_engine = create_engine(DOCTORS_DATABASE_URL)
DoctorsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctors_engine)
DoctorsBase = declarative_base()

def get_db():
    print("Inside database session verification")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_doctors_db():
    print("Inside doctors database session verification")
    db = DoctorsSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def create_doctors_tables():
    DoctorsBase.metadata.create_all(bind=doctors_engine)

create_doctors_tables()