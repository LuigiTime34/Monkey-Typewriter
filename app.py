from flask import Flask, render_template, jsonify, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import deque
from continuous_sim import continuous_sim
import threading
import random
import time
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monkey.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

current_state = {
    'running': False,
    'mode': None,
    'current_line': '',
    'context_lines': deque(maxlen=3),
    'target_text': '',
    'progress': {'line': 0, 'total_lines': 0},
    'time_started': None,
    'time_completed': None,
    'last_update': None,
    'total_attempts': 0,
    'total_correct_chars': 0,
    'is_completed': False
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class SimulationState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_text = db.Column(db.Text, nullable=False)
    current_progress = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_random_char():
    return chr(random.randint(32, 126))

def simulate_typing():
    global current_state
    
    while current_state['running']:
        if not current_state['target_text']:
            time.sleep(1)
            continue
            
        lines = current_state['target_text'].splitlines()
        line_num = current_state['progress']['line']
        
        if line_num >= len(lines):
            current_state['running'] = False
            current_state['is_completed'] = True
            current_state['time_completed'] = datetime.utcnow()
            break
            
        target_line = lines[line_num]
        current_pos = len(current_state['current_line'])
        
        if current_pos >= len(target_line):
            current_state['context_lines'].append(current_state['current_line'])
            current_state['current_line'] = ''
            current_state['progress']['line'] += 1
            continue
            
        target_char = target_line[current_pos]
        random_char = generate_random_char() if target_char != '\n' else '\n'
        
        current_state['total_attempts'] += 1
        if random_char == target_char:
            current_state['current_line'] += random_char
            current_state['total_correct_chars'] += 1
        elif current_state['mode'] == 'complex':
            current_state['current_line'] = ''
            
        current_state['last_update'] = datetime.utcnow()

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
    return jsonify({
        'running': continuous_sim.running,
        'mode': continuous_sim.mode,
        'current_line': continuous_sim.current_line,
        'progress': {
            'line': continuous_sim.line_number,
            'total_lines': len(continuous_sim.current_text.splitlines()) if continuous_sim.current_text else 0
        },
        'total_attempts': continuous_sim.total_attempts,
        'total_correct_chars': continuous_sim.total_correct_chars
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
