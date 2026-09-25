from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=True)
    seat = db.relationship("Seat", backref="employee", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "seat_id": self.seat.id if self.seat else None,
            "seat_label": self.seat.label if self.seat else None,
        }


class Seat(db.Model):
    __tablename__ = "seats"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "A1"
    floor = db.Column(db.String(50), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "floor": self.floor,
            "employee_id": self.employee_id,
            "employee_name": self.employee.name if self.employee else None,
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    prompt = db.Column(db.Text, nullable=True)
    action = db.Column(db.Text, nullable=False)
