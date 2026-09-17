from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from . import db

class WaterLevelSensor(db.Model):
    __tablename__ = "water_level_sensors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    echo: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger: Mapped[int] = mapped_column(Integer, nullable=False)
    resevoir_depth: Mapped[int] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)