"""Run once to populate sample data: python seed_data.py"""
from app import app
from models import db, Employee, Seat

SAMPLE_EMPLOYEES = [
    ("Sarah Johnson", "Engineering"),
    ("John Smith", "Design"),
    ("Alex Kim", "Engineering"),
    ("Priya Patel", "Marketing"),
    ("Michael Chen", "Sales"),
]

SAMPLE_SEATS = [
    ("A1", "3rd Floor"), ("A2", "3rd Floor"), ("A3", "3rd Floor"), ("A4", "3rd Floor"),
    ("B1", "3rd Floor"), ("B2", "3rd Floor"), ("B3", "3rd Floor"), ("B4", "3rd Floor"),
    ("C1", "4th Floor"), ("C2", "4th Floor"), ("C3", "4th Floor"), ("C4", "4th Floor"),
]

with app.app_context():
    db.create_all()

    if Employee.query.count() == 0:
        for name, dept in SAMPLE_EMPLOYEES:
            db.session.add(Employee(name=name, department=dept))

    if Seat.query.count() == 0:
        for label, floor in SAMPLE_SEATS:
            db.session.add(Seat(label=label, floor=floor))

    db.session.commit()

    # Assign the first few employees to seats so the grid isn't empty
    employees = Employee.query.order_by(Employee.id).all()
    seats = Seat.query.order_by(Seat.id).all()
    for emp, seat in zip(employees, seats):
        if seat.employee_id is None:
            seat.employee_id = emp.id
    db.session.commit()

    print(f"Seeded {Employee.query.count()} employees and {Seat.query.count()} seats.")
