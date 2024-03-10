from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def init_db():
    # Initialize database engine
    engine = create_engine('sqlite:///mydatabase.db')

    # Create a session factory
    Session = sessionmaker(bind=engine)

    return Session