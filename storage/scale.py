from sqlalchemy import Column, Integer, String, DateTime, Boolean
from base import Base
import datetime


class Scale(Base):
    """Scale"""

    __tablename__ = "scale"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    asteroid_id = Column(String(255), nullable=False)
    depth_cm = Column(Integer, nullable=False)
    estimated_kg_weight = Column(Integer, nullable=False)
    height_cm = Column(Integer, nullable=False)
    material = Column(String(255), nullable=False)
    record_id = Column(String(255), nullable=False)
    timestamp = Column(String(255), nullable=False)
    width_cm = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(255), nullable=False)

    def __init__(
        self,
        trace_id,
        asteroid_id,
        depth_cm,
        estimated_kg_weight,
        height_cm,
        material,
        record_id,
        timestamp,
        width_cm,
    ):
        """Initializes a direction reading"""

        self.trace_id = trace_id
        self.record_id = record_id
        self.asteroid_id = asteroid_id
        self.depth_cm = depth_cm
        self.estimated_kg_weight = estimated_kg_weight
        self.height_cm = height_cm
        self.material = material
        self.timestamp = timestamp
        self.width_cm = width_cm
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """Dictionary representation of a scale reading"""
        dictionary = {}
        dictionary["id"] = self.id
        dictionary["trace_id"] = self.trace_id
        dictionary["record_id"] = self.record_id
        dictionary["asteroid_id"] = self.asteroid_id
        dictionary["depth_cm"] = self.depth_cm
        dictionary["estimated_kg_weight"] = self.estimated_kg_weight
        dictionary["height_cm"] = self.height_cm
        dictionary["material"] = self.material
        dictionary["timestamp"] = self.timestamp
        dictionary["width_cm"] = self.width_cm
        dictionary["date_created"] = self.date_created

        return dictionary
