from app.database import SessionLocal
from app.models.employee import Employee
from app.auth.hashing import hash_password

db = SessionLocal()

admin = Employee(
    employee_id="ADMIN001",
    name="Shree",
    email="Shree@gmail.com",
    password=hash_password("Attendance@123"),
    department="Administration",
    designation="Administrator",
    is_admin=True,
    is_active=True,
    must_change_password=False,
)

db.add(admin)
db.commit()

print("Admin created successfully.")