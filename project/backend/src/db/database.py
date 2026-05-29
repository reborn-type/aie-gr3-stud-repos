from sqlalchemy import Column
from sqlalchemy.types import String, Text, Float, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Appeal(Base):
    __tablename__ = "appeals"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    percent_of_confidence: Mapped[float] = mapped_column(Float(), nullable=False)
    
