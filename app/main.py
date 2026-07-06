from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from fastapi.staticfiles import StaticFiles


# Import models
from app.models import Employee, Attendance

# Import routers
from app.routes.employee import router as employee_router
from app.routes.auth import router as auth_router
from app.routes.attendance import router as attendance_router
from app.routes.admin import router as admin_router
from app.routes.reports import router as reports_router
from app.routes import admin_charts

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Attendance Portal API",
    version="1.0.0"
)

# -----------------------------
# CORS Configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Register Routers
# -----------------------------
app.include_router(employee_router)
app.include_router(auth_router)
app.include_router(attendance_router)
app.include_router(admin_router)
app.include_router(reports_router)
app.include_router(admin_charts.router)

# -----------------------------
# Home Route
# -----------------------------

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

@app.get("/")
def home():
    return {
        "message": "Employee Attendance Portal Backend is Running 🚀"
    }

# -----------------------------
# Database Test
# -----------------------------
@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "Database Connected Successfully ✅"
        }
    except Exception as e:
        return {
            "error": str(e)
        }