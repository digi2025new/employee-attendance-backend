from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    department = Column(String)

    designation = Column(String)

    password = Column(String, nullable=False)

    must_change_password = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)

    is_admin = Column(Boolean, default=False)

    profile_picture = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship (MUST be inside the class)
    attendance = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )