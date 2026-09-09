from datetime import datetime
from sqlalchemy import DateTime, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db

class Job(db.Model):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pump_id: Mapped[int] = mapped_column(ForeignKey("pumps.id"), nullable=False)
    pump: Mapped["Pump"] = relationship()
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    function: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger: Mapped[str] = mapped_column(String(100), nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    args: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)