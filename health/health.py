from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Health(Base):
    """Health status of the applications"""

    __tablename__ = "health"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    receiver = Column(String(100), nullable=False)
    storage = Column(String(100), nullable=False)
    processing = Column(String(100), nullable=False)
    audit = Column(String(100), nullable=False)
    last_update = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, receiver, storage, processing, audit, last_update):
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit = audit
        self.last_update = last_update
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """Dictionary Representation of the status"""
        dict = {}
        dict["id"] = self.id
        dict["receiver"] = self.receiver
        dict["storage"] = self.storage
        dict["processing"] = self.processing
        dict["audit"] = self.audit
        dict["last_update"] = self.last_update
        dict["date_created"] = self.date_created

        return dict
