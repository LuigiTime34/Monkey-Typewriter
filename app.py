from flask import Flask, render_template, jsonify, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required
from werkzeug.security import check_password_hash
import threading
import os
from models import db, User, SimulationState
import datetime

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monkey.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import simulation after app is created
from simulation import continuous_sim

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))
    
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/api/start', methods=['POST'])
@login_required
def start_simulation():
    data = request.get_json()
    target_text = data.get('text', '')
    mode = data.get('mode', 'simple')
    
    if not target_text:
        return jsonify({'error': 'No text provided'}), 400
        
    continuous_sim.start(target_text, mode)
    return jsonify({'status': 'success'})

@app.route('/api/stop', methods=['POST'])
@login_required
def stop_simulation():
    continuous_sim.stop()
    return jsonify({'status': 'success'})

@app.route('/api/status')
def get_status():
    elapsed_time = 0
    if continuous_sim.time_started:
        current_time = datetime.utcnow()
        elapsed_time = (current_time - continuous_sim.time_started).total_seconds()
    
    completion_time = None
    if continuous_sim.time_completed:
        completion_time = (continuous_sim.time_completed - continuous_sim.time_started).total_seconds()
    
    return jsonify({
        'running': continuous_sim.running,
        'mode': continuous_sim.mode,
        'current_line': continuous_sim.current_line,
        'context_lines': continuous_sim.context_lines,
        'progress': {
            'line': continuous_sim.line_number,
            'total_lines': len(continuous_sim.current_text.splitlines()) if continuous_sim.current_text else 0
        },
        'elapsed_seconds': elapsed_time,
        'completion_seconds': completion_time,
        'total_attempts': continuous_sim.total_attempts,
        'total_correct_chars': continuous_sim.total_correct_chars,
        'time_started': continuous_sim.time_started.isoformat() if continuous_sim.time_started else None,
        'time_completed': continuous_sim.time_completed.isoformat() if continuous_sim.time_completed else None,
        'target_text': continuous_sim.current_text
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)