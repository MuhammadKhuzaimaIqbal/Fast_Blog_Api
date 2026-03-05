from app.config import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Boolean

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True) 
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.user, nullable=False)