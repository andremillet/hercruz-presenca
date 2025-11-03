from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from models import db, User, Shift, Attendance
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import qrcode
import io
import socket
from pytz import timezone

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# Timezone setup
sao_paulo_tz = timezone('America/Sao_Paulo')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hercruz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production

db.init_app(app)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

@app.route('/')
def index():
    return render_template('index.html')

# Basic auth routes (placeholder for now)
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(name=data['name'], email=data['email'], role=data['role'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# Shifts CRUD
@app.route('/api/shifts', methods=['GET'])
def get_shifts():
    shifts = Shift.query.all()
    return jsonify([{
        'id': s.id,
        'date': s.date.isoformat(),
        'type': s.type,
        'nurse_group': s.nurse_group,
        'assigned_users': s.assigned_users
    } for s in shifts])

@app.route('/api/shifts', methods=['POST'])
def create_shift():
    data = request.get_json()
    new_shift = Shift(
        date=datetime.fromisoformat(data['date']),
        type=data['type'],
        nurse_group=data.get('nurse_group'),
        assigned_users=data.get('assigned_users', '')
    )
    db.session.add(new_shift)
    db.session.commit()
    return jsonify({'message': 'Shift created', 'id': new_shift.id}), 201

@app.route('/api/shifts/<int:id>', methods=['PUT'])
def update_shift(id):
    shift = Shift.query.get_or_404(id)
    data = request.get_json()
    shift.date = datetime.fromisoformat(data.get('date', shift.date.isoformat()))
    shift.type = data.get('type', shift.type)
    shift.nurse_group = data.get('nurse_group', shift.nurse_group)
    shift.assigned_users = data.get('assigned_users', shift.assigned_users)
    db.session.commit()
    return jsonify({'message': 'Shift updated'})

@app.route('/api/shifts/<int:id>', methods=['DELETE'])
def delete_shift(id):
    shift = Shift.query.get_or_404(id)
    db.session.delete(shift)
    db.session.commit()
    return jsonify({'message': 'Shift deleted'})

# Attendance API
@app.route('/api/attendance/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    user_id = data['user_id']
    shift_id = data['shift_id']
    check_in_time = datetime.now(sao_paulo_tz)
    attendance = Attendance(user_id=user_id, shift_id=shift_id, check_in=check_in_time)
    db.session.add(attendance)
    db.session.commit()
    return jsonify({'message': 'Check-in recorded', 'id': attendance.id}), 201

@app.route('/api/attendance/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    attendance_id = data['attendance_id']
    check_out_time = datetime.now(sao_paulo_tz)
    attendance = Attendance.query.get_or_404(attendance_id)
    attendance.check_out = check_out_time
    if attendance.check_in:
        delta = check_out_time - attendance.check_in
        attendance.hours_worked = delta.total_seconds() / 3600
    db.session.commit()
    return jsonify({'message': 'Check-out recorded'})

# QR Code generation
@app.route('/api/qr', methods=['GET'])
def generate_qr():
    # Generate QR with URL to the app
    qr_data = "https://aa6075a1ae9c.ngrok-free.app?scan=true"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# CPF validation and registration
@app.route('/api/auth/validate_cpf', methods=['POST'])
def validate_cpf():
    data = request.get_json()
    cpf = data['cpf']
    user = User.query.filter_by(cpf=cpf).first()
    if user:
        # Record check-in for default shift
        default_shift = Shift.query.first()
        if default_shift:
            attendance = Attendance(user_id=user.id, shift_id=default_shift.id, check_in=datetime.utcnow())
            db.session.add(attendance)
            db.session.commit()
        return jsonify({'exists': True, 'user_id': user.id})
    else:
        return jsonify({'exists': False})

@app.route('/api/auth/register_cpf', methods=['POST'])
def register_cpf():
    data = request.get_json()
    cpf = data['cpf']
    name = data['name']
    crm = data.get('crm')
    # For simplicity, create user with default email and password
    email = f"{cpf}@hercruz.com"
    hashed_password = generate_password_hash('defaultpass')  # Change later
    role = 'plantonista'  # Default
    new_user = User(name=name, email=email, cpf=cpf, crm=crm, role=role, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered', 'user_id': new_user.id}), 201

@app.route('/api/attendance', methods=['GET'])
def get_attendances():
    attendances = Attendance.query.all()
    result = []
    for a in attendances:
        user = User.query.get(a.user_id)
        user_name = user.name if user else 'Desconhecido'
        result.append({
            'id': a.id,
            'user_id': a.user_id,
            'user_name': user_name,
            'shift_id': a.shift_id,
            'check_in': a.check_in.isoformat() if a.check_in else None,
            'check_out': a.check_out.isoformat() if a.check_out else None,
            'hours_worked': a.hours_worked
        })
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # For dev, drop and recreate
        db.create_all()
        # Create a default shift if none exists
        if not Shift.query.first():
            default_shift = Shift(
                date=datetime.now(sao_paulo_tz).date(),
                type='day_shift',
                nurse_group='3-4',
                assigned_users='[]'
            )
            db.session.add(default_shift)
            db.session.commit()
        # Create default user if none exists
        if not User.query.first():
            hashed_password = generate_password_hash('defaultpass')
            default_user = User(
                name='ANDRE BATISTA MILLET NEVES',
                email='andre@hercruz.com',
                cpf='11432651730',
                crm='52946788',
                role='plantonista',
                password=hashed_password
            )
            db.session.add(default_user)
            db.session.commit()
            # Create default attendance for demo
            default_attendance = Attendance(
                user_id=default_user.id,
                shift_id=default_shift.id,
                check_in=datetime.now(sao_paulo_tz)
            )
            db.session.add(default_attendance)
            db.session.commit()
            db.session.add(default_user)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)