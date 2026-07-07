from app.database import SessionLocal
from app.models.employee import Employee
from app.auth.hashing import hash_password

db = SessionLocal()

# ==========================
# Admin Details
# ==========================

ADMIN_EMAIL = "Shree@gmail.com"
ADMIN_PASSWORD = "Attendance@123"

# ==========================
# Check if admin already exists
# ==========================

existing_admin = db.query(Employee).filter(
    Employee.email == ADMIN_EMAIL
).first()

if existing_admin:
    print("✅ Admin already exists!")
    print(f"Email: {ADMIN_EMAIL}")

else:
    admin = Employee(
        employee_id="ADMIN001",
        name="Shree",
        email=ADMIN_EMAIL,
        password=hash_password(ADMIN_PASSWORD),
        department="Administration",
        designation="Administrator",
        is_admin=True,
        is_active=True,
        must_change_password=False,
    )

    db.add(admin)
    db.commit()

    print("====================================")
    print("✅ Admin created successfully!")
    print(f"Email    : {ADMIN_EMAIL}")
    print(f"Password : {ADMIN_PASSWORD}")
    print("====================================")

db.close()