from sqlalchemy.orm import Session
import dbmodels
from typing import List


def get_client(db: Session, client_id: int) -> dbmodels.Client:
    return db.query(dbmodels.DBClient).filter(dbmodels.DBClient.id == client_id).first()


def get_all_clients(db: Session, skip: int = 0, limit: int = 100) -> List[dbmodels.Client]:
    return db.query(dbmodels.DBClient).offset(skip).limit(limit).all()
