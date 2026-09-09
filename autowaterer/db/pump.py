from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from . import db

class Pump(db.Model):
    __tablename__ = "pumps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    gpio_pin: Mapped[int] = mapped_column(Integer, nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)