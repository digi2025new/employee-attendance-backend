from fastapi import UploadFile, File
from pathlib import Path
import shutil
import uuid

from app.auth.dependencies import get_current_employee
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from app.auth.hashing import hash_password

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


# ===========================
# Create Employee
# ===========================
@router.post("/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):

    existing = db.query(Employee).filter(
        Employee.email == employee.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    total = db.query(Employee).count() + 1
    employee_id = f"EMP{total:03d}"

    new_employee = Employee(
        employee_id=employee_id,
        name=employee.name,
        email=employee.email,
        department=employee.department,
        designation=employee.designation,
        password=hash_password(employee.email),
        must_change_password=True,
        is_active=True,
        is_admin=False
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
    "message": "Employee Created Successfully",
    "employee_id": employee_id,
    "default_password": employee.email
}


# ===========================
# Update Employee
# ===========================
@router.put("/{employee_id}")
def update_employee(
    employee_id: str,
    department: str,
    designation: str,
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

    employee.department = department
    employee.designation = designation

    db.commit()

    return {
        "message": "Employee Updated Successfully"
    }


# ===========================
# Deactivate Employee
# ===========================
@router.delete("/{employee_id}")
def deactivate_employee(
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

    employee.is_active = False

    db.commit()

    return {
        "message": "Employee Deactivated Successfully"
    }

# ===========================
# Employee Profile
# ===========================
@router.get("/profile")
def get_profile(
    current_employee: Employee = Depends(get_current_employee)
):
    return {
        "employee_id": current_employee.employee_id,
        "name": current_employee.name,
        "email": current_employee.email,
        "department": current_employee.department,
        "designation": current_employee.designation,
        "is_active": current_employee.is_active,
        "is_admin": current_employee.is_admin,
        "profile_picture": current_employee.profile_picture,
    }

@router.post("/employee/upload-profile-picture")
def upload_profile_picture(
    employee_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    # Create upload directory
    upload_dir = Path("uploads/profile_pictures")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"

    file_path = upload_dir / filename

    # Save image
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save path in database
    employee.profile_picture = f"/uploads/profile_pictures/{filename}"

    db.commit()
    db.refresh(employee)

    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture": employee.profile_picture,
    }