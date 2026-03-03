from app.config import Base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class Blog(Base):
    __tablename__ = "blogs"

    id : Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]= mapped_column (String(30),nullable=False)
    content: Mapped[str]= mapped_column(String(100),nullable=False)
    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum),default=StatusEnum.pending,nullable=False)