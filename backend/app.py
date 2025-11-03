from flask import Flask, request, jsonify, send_file, render_template, session, redirect, url_for
from flask_cors import CORS
from models import db, User, Shift, Attendance
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import qrcode
import io
import socket
from pytz import timezone

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)
app.secret_key = 'admin-secret-key'  # Change in production

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
    now = datetime.now(sao_paulo_tz)

    # Check if already checked in within the last 12 hours from 7 AM
    # Periods: 7 AM - 7 PM, 7 PM - 7 AM next day
    if now.hour >= 7 and now.hour < 19:  # 7 AM to 7 PM
        period_start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    else:  # 7 PM to 7 AM
        if now.hour >= 19:
            period_start = now.replace(hour=19, minute=0, second=0, microsecond=0)
        else:
            yesterday = now - timedelta(days=1)
            period_start = yesterday.replace(hour=19, minute=0, second=0, microsecond=0)

    period_end = period_start + timedelta(hours=12)

    existing = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.check_in >= period_start,
        Attendance.check_in < period_end
    ).first()

    if existing:
        return jsonify({'message': 'Já fez check-in neste período de 12 horas.'}), 400

    check_in_time = now
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

@app.route('/admin')
def admin():
    if session.get('admin_logged_in'):
        return render_template('admin.html')
    else:
        return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.role == 'admin' and check_password_hash(user.password, data['password']):
        session['admin_logged_in'] = True
        if data['password'] == 'admin':
            return jsonify({'first_login': True, 'message': 'Troque a senha no painel.'})
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Credenciais inválidas'}), 401

@app.route('/admin/change_password', methods=['POST'])
def change_password():
    if not session.get('admin_logged_in'):
        return jsonify({'message': 'Não logado'}), 401
    data = request.get_json()
    user = User.query.filter_by(email='admin@hercruz.com').first()
    user.password = generate_password_hash(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Senha alterada'})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

@app.route('/admin/reports')
def admin_reports():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    report_type = request.args.get('type', 'daily')  # daily or monthly
    scope = request.args.get('scope', 'general')  # general or user
    user_id = request.args.get('user_id')
    
    # Filtrar attendances
    attendances = Attendance.query
    if scope == 'user' and user_id:
        attendances = attendances.filter_by(user_id=user_id)
    now = datetime.now(sao_paulo_tz)
    if report_type == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        attendances = attendances.filter(Attendance.check_in >= start_date)
    elif report_type == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        attendances = attendances.filter(Attendance.check_in >= start_date)
    
    attendances = attendances.all()
    
    # Usuários para dropdown
    users = User.query.all()
    
    # Gerar HTML do relatório
    user_options = "".join(f'<option value="{u.id}">{u.name}</option>' for u in users)
    table_rows = "".join(f"""
    <tr>
        <td>{a.user.name if a.user else 'Desconhecido'}</td>
        <td>{a.check_in.strftime('%d/%m/%Y %H:%M') if a.check_in else 'N/A'}</td>
        <td>{a.check_out.strftime('%d/%m/%Y %H:%M') if a.check_out else 'N/A'}</td>
        <td>{f"{a.hours_worked:.2f}" if a.hours_worked else 'N/A'}</td>
    </tr>""" for a in attendances)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Frequência</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            @media print {{ body {{ margin: 0; }} }}
        </style>
    </head>
    <body>
        <h1>Relatório de Frequência {report_type.capitalize()} - {scope.capitalize()}</h1>
        <form method="get">
            <label>Tipo: 
                <select name="type">
                    <option value="daily" {'selected' if report_type == 'daily' else ''}>Diário</option>
                    <option value="monthly" {'selected' if report_type == 'monthly' else ''}>Mensal</option>
                </select>
            </label>
            <label>Escopo: 
                <select name="scope">
                    <option value="general" {'selected' if scope == 'general' else ''}>Geral</option>
                    <option value="user" {'selected' if scope == 'user' else ''}>Por Usuário</option>
                </select>
            </label>
            <select name="user_id" style="display: {'block' if scope == 'user' else 'none'};">
                <option value="">Selecione Usuário</option>
                {user_options}
            </select>
            <button type="submit">Gerar</button>
        </form>
        <table>
            <tr><th>Usuário</th><th>Check-in</th><th>Check-out</th><th>Horas Trabalhadas</th></tr>
            {table_rows}
        </table>
        <button onclick="window.print()">Imprimir</button>
        <a href="/admin">Voltar ao Painel</a>
    </body>
    </html>
    """
    return html

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

        # Create admin user if not exists
        if not User.query.filter_by(email='admin@hercruz.com').first():
            hashed_password = generate_password_hash('admin')
            admin_user = User(
                name='Administrador',
                email='admin@hercruz.com',
                cpf='admin',
                role='admin',
                password=hashed_password
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)