import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

from db.database import Appeal
from settings import get_env_path

load_dotenv(get_env_path())

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_appeals():
    with SessionLocal() as session:
        result = session.execute(select(Appeal))
        return result.scalars().all()
    
def get_appeal_by_id(appeal_id):
    with SessionLocal() as session:
        return session.get(Appeal, appeal_id)
    
def create_appeal(title: str, text: str, department: str, percent_of_confidence: float):
    with SessionLocal() as session:
        appeal = Appeal(
            title=title,
            text=text,
            department=department,
            percent_of_confidence=percent_of_confidence,
        )
        
        session.add(appeal)
        session.commit()
        session.refresh(appeal)

        return appeal
    
def delete_appeals():
    with SessionLocal() as session:
        session.execute(delete(Appeal))
        session.commit()
        return {"message": "Все обращения удалены"}
    

def delete_appeal_by_id(appeal_id:int):
    with SessionLocal() as session:
        appeal = session.get(Appeal, appeal_id)
        
        if appeal is None: 
            return None
        
        deleted_appeal = {
            "id": appeal.id,
            "title": appeal.title,
            "text": appeal.text, 
            "department": appeal.department,
            "percent_of_confidence": appeal.percent_of_confidence,
        }
        
        session.delete(appeal)
        session.commit()
        
        return deleted_appeal
