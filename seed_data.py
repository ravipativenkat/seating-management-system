"""Seed sample data for the seating management system."""

from models import db, Employee, Seat


SAMPLE_EMPLOYEES = [
    ("Sarah Johnson", "Engineering"),
    ("John Smith", "Design"),
    ("Alex Kim", "Engineering"),
    ("Priya Patel", "Marketing"),
    ("Michael Chen", "Sales"),
]

SAMPLE_SEATS = [
    ("A1", "3rd Floor"),
    ("A2", "3rd Floor"),
    ("A3", "3rd Floor"),
    ("A4", "3rd Floor"),
    ("B1", "3rd Floor"),
    ("B2", "3rd Floor"),
    ("B3", "3rd Floor"),
    ("B4", "3rd Floor"),
    ("C1", "4th Floor"),
    ("C2", "4th Floor"),
    ("C3", "4th Floor"),
    ("C4", "4th Floor"),
]


def seed_database():
    """Add sample data when the database is empty."""
    employees_before = Employee.query.count()
    seats_before = Seat.query.count()

    if employees_before == 0:
        for name, department in SAMPLE_EMPLOYEES:
            db.session.add(
                Employee(name=name, department=department)
            )

    if seats_before == 0:
        for label, floor in SAMPLE_SEATS:
            db.session.add(
                Seat(label=label, floor=floor)
            )

    db.session.commit()

    # Assign demo employees only when starting with a completely empty database.
    # This prevents re-running the seed process from changing existing assignments.
    if employees_before == 0 and seats_before == 0:
        employees = Employee.query.order_by(Employee.id).all()
        seats = Seat.query.order_by(Seat.id).all()

        for employee, seat in zip(employees, seats):
            if seat.employee_id is None:
                seat.employee_id = employee.id

        db.session.commit()

    return Employee.query.count(), Seat.query.count()


if __name__ == "__main__":
    # Keep the standalone `python seed_data.py` command working.
    from app import app

    with app.app_context():
        db.create_all()
        employee_count, seat_count = seed_database()
        print(
            f"Seeded {employee_count} employees and "
            f"{seat_count} seats."
        )