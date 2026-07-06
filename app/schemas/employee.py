from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    designation: str


class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: str | None = None
    designation: str | None = None
    profile_picture: str | None = None

    class Config:
        from_attributes = True


class EmployeeUpdate(BaseModel):
    name: str
    department: str
    designation: str