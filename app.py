import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from models import db, Employee, Seat, ActivityLog
from ai_assistant import interpret_prompt, AIAssistantError

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'seating.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

db.init_app(app)

with app.app_context():
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    db.create_all()


# ---------- Pages ----------

@app.route("/")
def index():
    seats = Seat.query.order_by(Seat.label).all()
    return render_template("index.html", seats=seats)


@app.route("/admin")
def admin():
    employees = Employee.query.order_by(Employee.name).all()
    seats = Seat.query.order_by(Seat.label).all()
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(15).all()
    return render_template("admin.html", employees=employees, seats=seats, logs=logs)


# ---------- JSON API ----------

@app.route("/api/seats")
def api_seats():
    return jsonify([s.to_dict() for s in Seat.query.order_by(Seat.label).all()])


@app.route("/api/employees")
def api_employees():
    return jsonify([e.to_dict() for e in Employee.query.order_by(Employee.name).all()])


@app.route("/api/employees", methods=["POST"])
def api_add_employee():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    department = (data.get("department") or "").strip()
    if not name:
        return jsonify({"error": "Employee name is required."}), 400
    emp = Employee(name=name, department=department)
    db.session.add(emp)
    db.session.commit()
    return jsonify(emp.to_dict()), 201


@app.route("/api/seats", methods=["POST"])
def api_add_seat():
    data = request.get_json(force=True)
    label = (data.get("label") or "").strip()
    floor = (data.get("floor") or "").strip()
    if not label:
        return jsonify({"error": "Seat label is required."}), 400
    if Seat.query.filter_by(label=label).first():
        return jsonify({"error": f"Seat '{label}' already exists."}), 400
    seat = Seat(label=label, floor=floor)
    db.session.add(seat)
    db.session.commit()
    return jsonify(seat.to_dict()), 201


@app.route("/api/assign", methods=["POST"])
def api_assign():
    """Manual assignment: {employee_id, seat_label} or {employee_id, seat_label: null} to unassign."""
    data = request.get_json(force=True)
    employee_id = data.get("employee_id")
    seat_label = data.get("seat_label")

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found."}), 404

    result = _apply_assignment(employee, seat_label)
    db.session.add(ActivityLog(prompt=None, action=result["message"]))
    db.session.commit()
    return jsonify(result)


@app.route("/api/ai-assist", methods=["POST"])
def api_ai_assist():
    """Admin types a natural-language prompt; AI extracts the action and we execute it."""
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        action = interpret_prompt(prompt)
    except AIAssistantError as e:
        return jsonify({"error": str(e)}), 400

    employee_name = (action.get("employee") or "").strip()
    seat_label = action.get("seat")
    act_type = action.get("action")

    employee = Employee.query.filter(Employee.name.ilike(f"%{employee_name}%")).first()
    if not employee:
        return jsonify({"error": f"No employee matching '{employee_name}' found."}), 404

    seat_label_to_apply = None if act_type == "unassign" else seat_label
    result = _apply_assignment(employee, seat_label_to_apply)

    log = ActivityLog(prompt=prompt, action=result["message"])
    db.session.add(log)
    db.session.commit()

    result["interpreted_action"] = action
    return jsonify(result)


def _apply_assignment(employee: Employee, seat_label):
    """Free the employee's current seat, then assign the new one (or leave unassigned)."""
    # Free any seat currently held by this employee
    current_seat = Seat.query.filter_by(employee_id=employee.id).first()
    if current_seat:
        current_seat.employee_id = None

    if not seat_label:
        db.session.commit()
        return {"message": f"{employee.name} unassigned from any seat.", "employee": employee.to_dict()}

    seat = Seat.query.filter(Seat.label.ilike(seat_label)).first()
    if not seat:
        db.session.commit()  # keep the unassign from above
        return {"error": f"Seat '{seat_label}' does not exist.", "message": f"Could not find seat '{seat_label}'."}

    if seat.employee_id and seat.employee_id != employee.id:
        previous = Employee.query.get(seat.employee_id)
        seat.employee_id = None
        db.session.flush()
        message_prefix = f"Seat {seat.label} was freed from {previous.name}. "
    else:
        message_prefix = ""

    seat.employee_id = employee.id
    db.session.commit()
    return {
        "message": f"{message_prefix}{employee.name} assigned to seat {seat.label}.",
        "employee": employee.to_dict(),
        "seat": seat.to_dict(),
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
