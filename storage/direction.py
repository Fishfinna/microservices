from sqlalchemy import Column, Integer, String, DateTime, Boolean
from base import Base
import datetime


class Direction(Base):
    """Direction"""

    __tablename__ = "direction"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    asteroid_id = Column(String(255), nullable=False)
    collision_risk = Column(Boolean, nullable=False)
    direction = Column(Integer, nullable=False)
    km_per_hour = Column(Integer, nullable=False)
    moving_towards_earth = Column(Boolean, nullable=False)
    record_id = Column(String(250), nullable=False, primary_key=True)
    timestamp = Column(String(255), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(255), nullable=False)

    def __init__(
        self,
        trace_id,
        asteroid_id,
        collision_risk,
        direction,
        km_per_hour,
        moving_towards_earth,
        record_id,
        timestamp,
    ):
        """Initializes a direction reading"""

        self.trace_id = trace_id
        self.record_id = record_id
        self.asteroid_id = asteroid_id
        self.collision_risk = collision_risk
        self.direction = direction
        self.km_per_hour = km_per_hour
        self.moving_towards_earth = moving_towards_earth
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """Dictionary representation of a direction reading"""
        dictionary = {}
        dictionary["id"] = self.id
        dictionary["trace_id"] = self.trace_id
        dictionary["record_id"] = self.record_id
        dictionary["asteroid_id"] = self.asteroid_id
        dictionary["collision_risk"] = self.collision_risk
        dictionary["direction"] = self.direction
        dictionary["km_per_hour"] = self.km_per_hour
        dictionary["moving_towards_earth"] = self.moving_towards_earth
        dictionary["timestamp"] = self.timestamp
        dictionary["date_created"] = self.date_created

        return dictionary
