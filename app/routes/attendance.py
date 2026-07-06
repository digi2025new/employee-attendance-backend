from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.auth.dependencies import get_current_employee

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

# =====================================
# Company Attendance Policy
# =====================================

FULL_DAY_HOURS = 8
HALF_DAY_HOURS = 4


# =====================================
# Punch In
# =====================================

@router.post("/punch-in")
def punch_in(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    today = date.today()

    existing = db.query(Attendance).filter(
        Attendance.employee_id == current_employee.employee_id,
        Attendance.date == today
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already punched in today"
        )

    attendance = Attendance(
        employee_id=current_employee.employee_id,
        date=today,
        punch_in=datetime.now()
    )

    db.add(attendance)
    db.commit()

    return {
        "message": "Punch In Successful"
    }


# =====================================
# Punch Out
# =====================================

@router.post("/punch-out")
def punch_out(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    today = date.today()

    attendance = db.query(Attendance).filter(
        Attendance.employee_id == current_employee.employee_id,
        Attendance.date == today
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Punch In not found"
        )

    if attendance.punch_out:
        raise HTTPException(
            status_code=400,
            detail="Already punched out"
        )

    attendance.punch_out = datetime.now()

    total = attendance.punch_out - attendance.punch_in

    hours = round(total.total_seconds() / 3600, 2)

    attendance.working_hours = str(hours)

    # =====================================
    # Attendance Status
    # =====================================

    if hours >= FULL_DAY_HOURS:
        attendance.attendance_status = "Present"

    elif hours >= HALF_DAY_HOURS:
        attendance.attendance_status = "Half Day"

    else:
        attendance.attendance_status = "Absent"

    db.commit()

    return {
        "message": "Punch Out Successful",
        "working_hours": hours,
        "status": attendance.attendance_status
    }


# =====================================
# Attendance History
# =====================================

@router.get("/history")
def history(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    attendance = db.query(Attendance).filter(
        Attendance.employee_id == current_employee.employee_id
    ).all()

    return attendance