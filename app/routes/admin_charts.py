from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.auth.dependencies import get_current_employee

router = APIRouter(
    prefix="/admin/charts",
    tags=["Admin Charts"]
)


# -----------------------------
# Attendance Overview
# -----------------------------
@router.get("/attendance")
def attendance_chart(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db)
):

    present = db.query(Attendance).filter(
        Attendance.attendance_status == "Present"
    ).count()

    half_day = db.query(Attendance).filter(
        Attendance.attendance_status == "Half Day"
    ).count()

    absent = db.query(Attendance).filter(
        Attendance.attendance_status == "Absent"
    ).count()

    return [
        {
            "name": "Present",
            "value": present
        },
        {
            "name": "Half Day",
            "value": half_day
        },
        {
            "name": "Absent",
            "value": absent
        }
    ]


# -----------------------------
# Department Wise Employees
# -----------------------------
@router.get("/departments")
def department_chart(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db)
):

    data = (
        db.query(
            Employee.department,
            func.count(Employee.id)
        )
        .group_by(Employee.department)
        .all()
    )

    return [
        {
            "department": department,
            "employees": total
        }
        for department, total in data
    ]