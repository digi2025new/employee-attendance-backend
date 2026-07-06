from pydantic import BaseModel, EmailStr

class Login(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str