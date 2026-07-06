from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session
from sqlalchemy import extract

from openpyxl import Workbook
from openpyxl.styles import Font

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# ---------------- Excel Report ---------------- #

@router.get("/excel/{month}")
def export_excel(month: int, db: Session = Depends(get_db)):

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"

    headers = [
        "Employee ID",
        "Employee Name",
        "Email",
        "Date",
        "Punch In",
        "Punch Out",
        "Working Hours",
        "Attendance Status"
    ]

    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True)

    records = (
        db.query(Attendance, Employee)
        .join(
            Employee,
            Attendance.employee_id == Employee.employee_id
        )
        .filter(
            extract("month", Attendance.date) == month
        )
        .all()
    )

    for attendance, employee in records:

        sheet.append([
            employee.employee_id,
            employee.name,
            employee.email,
            str(attendance.date),
            str(attendance.punch_in) if attendance.punch_in else "-",
            str(attendance.punch_out) if attendance.punch_out else "-",
            attendance.working_hours or "-",
            attendance.attendance_status or "-"
        ])

    # Auto-size columns
    for column in sheet.columns:
        length = max(len(str(cell.value)) for cell in column)
        sheet.column_dimensions[column[0].column_letter].width = length + 5

    filename = f"attendance_month_{month}.xlsx"

    workbook.save(filename)

    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )


# ---------------- PDF Report ---------------- #

@router.get("/pdf/{month}")
def export_pdf(month: int, db: Session = Depends(get_db)):

    filename = f"attendance_month_{month}.pdf"

    document = SimpleDocTemplate(filename)

    data = [[
        "Employee ID",
        "Name",
        "Email",
        "Date",
        "Punch In",
        "Punch Out",
        "Hours",
        "Status"
    ]]

    records = (
        db.query(Attendance, Employee)
        .join(
            Employee,
            Attendance.employee_id == Employee.employee_id
        )
        .filter(
            extract("month", Attendance.date) == month
        )
        .all()
    )

    for attendance, employee in records:

        data.append([
            employee.employee_id,
            employee.name,
            employee.email,
            str(attendance.date),
            str(attendance.punch_in) if attendance.punch_in else "-",
            str(attendance.punch_out) if attendance.punch_out else "-",
            attendance.working_hours or "-",
            attendance.attendance_status or "-"
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))

    document.build([table])

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )