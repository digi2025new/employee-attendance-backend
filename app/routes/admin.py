from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance

from app.schemas.employee import EmployeeUpdate
from fastapi import HTTPException

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# =========================
# DASHBOARD
# =========================
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):

    total_employees = db.query(Employee).count()
    today = date.today()

    present_today = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.attendance_status == "Present"
    ).count()

    absent_today = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.attendance_status == "Absent"
    ).count()

    half_day = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.attendance_status == "Half Day"
    ).count()

    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "half_day": half_day
    }

# =========================
# EMPLOYEES
# =========================
@router.get("/employees")
def get_all_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

# =========================
# ATTENDANCE
# =========================
@router.get("/attendance")
def get_all_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).all()

# =========================
# MONTHLY ATTENDANCE
# =========================
@router.get("/attendance/month/{month}")
def monthly_attendance(month: int, db: Session = Depends(get_db)):

    return db.query(Attendance).filter(
        extract("month", Attendance.date) == month
    ).all()

# =========================
# ATTENDANCE DETAILS (FILTER)
# =========================
@router.get("/attendance-details")
def attendance_details(
    month: int | None = Query(None),
    attendance_date: date | None = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(Attendance).options(
        joinedload(Attendance.employee)
    )

    if month:
        query = query.filter(
            extract("month", Attendance.date) == month
        )

    if attendance_date:
        query = query.filter(
            Attendance.date == attendance_date
        )

    records = query.order_by(Attendance.date.desc()).all()

    return [
        {
            "id": a.id,
            "employee_id": a.employee.employee_id,
            "name": a.employee.name,
            "email": a.employee.email,
            "date": a.date,
            "punch_in": a.punch_in,
            "punch_out": a.punch_out,
            "working_hours": a.working_hours,
            "attendance_status": a.attendance_status,
        }
        for a in records
    ]

# =========================
# TOGGLE EMPLOYEE ACTIVE/INACTIVE
# =========================
@router.put("/employee/{employee_id}/toggle")
def toggle_employee(employee_id: str, db: Session = Depends(get_db)):

    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if not employee:
        return {"error": "Employee not found"}

    employee.is_active = not employee.is_active
    db.commit()

    return {
        "message": "Employee status updated",
        "is_active": employee.is_active
    }

@router.put("/employee/{employee_id}")
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee.name = data.name
    employee.department = data.department
    employee.designation = data.designation

    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee updated successfully"
    }

@router.delete("/employee/{employee_id}")
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Delete employee attendance first
    db.query(Attendance).filter(
        Attendance.employee_id == employee_id
    ).delete()

    # Delete employee
    db.delete(employee)

    db.commit()

    return {
        "message": "Employee deleted successfully"
    }