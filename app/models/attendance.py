from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=False,
    )

    date = Column(Date, nullable=False)

    punch_in = Column(DateTime)

    punch_out = Column(DateTime)

    working_hours = Column(String, default="0")

    attendance_status = Column(String, default="Pending")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationship (MUST be inside the class)
    employee = relationship(
        "Employee",
        back_populates="attendance",
    )