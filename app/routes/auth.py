from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.employee import Employee
from app.auth.hashing import verify_password, hash_password
from app.auth.jwt_handler import create_access_token
from app.schemas.auth import ChangePassword


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# Forgot Password Schema
# =========================

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.email == form_data.username
    ).first()

    if not employee:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    if not verify_password(
        form_data.password,
        employee.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    token = create_access_token(
        data={
            "sub": employee.email,
            "employee_id": employee.employee_id,
            "is_admin": employee.is_admin
        },
        expires_delta=timedelta(days=1)
    )

    return {
    "access_token": token,
    "token_type": "bearer",
    "employee_id": employee.employee_id,
    "name": employee.name,
    "email": employee.email,
    "is_admin": employee.is_admin,
    "must_change_password": employee.must_change_password
}


# =========================
# CHANGE PASSWORD
# =========================

@router.post("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.email == data.email
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if not verify_password(
        data.old_password,
        employee.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Old password is incorrect"
        )

    employee.password = hash_password(
        data.new_password
    )

    employee.must_change_password = False

    db.commit()

    return {
        "message": "Password changed successfully"
    }


# =========================
# FORGOT PASSWORD
# =========================

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.email == request.email
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    employee.password = hash_password(
        request.new_password
    )

    employee.must_change_password = False

    db.commit()

    return {
        "message": "Password updated successfully"
    }