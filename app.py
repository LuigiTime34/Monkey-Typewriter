from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import time
import random
import os
from collections import deque
import json
from datetime import datetime

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
    global current_state
    
    data = request.get_json()
    target_text = data.get('text', '')
    mode = data.get('mode', 'simple')
    
    if not target_text:
        return jsonify({'error': 'No text provided'}), 400
        
    current_state['target_text'] = target_text
    current_state['mode'] = mode
    current_state['progress'] = {'line': 0, 'total_lines': len(target_text.splitlines())}
    current_state['current_line'] = ''
    current_state['context_lines'].clear()
    current_state['time_started'] = datetime.utcnow()
    current_state['time_completed'] = None
    current_state['total_attempts'] = 0
    current_state['total_correct_chars'] = 0
    current_state['is_completed'] = False
    
    if not current_state['running']:
        current_state['running'] = True
        threading.Thread(target=simulate_typing, daemon=True).start()
    
    return jsonify({'status': 'success'})

@app.route('/api/stop', methods=['POST'])
@login_required
def stop_simulation():
    global current_state
    current_state['running'] = False
    return jsonify({'status': 'success'})

@app.route('/api/status')
def get_status():
    elapsed_time = 0
    if current_state['time_started']:
        elapsed_time = (datetime.utcnow() - current_state['time_started']).total_seconds()
    
    completion_time = None
    if current_state['time_completed']:
        completion_time = (current_state['time_completed'] - current_state['time_started']).total_seconds()
    
    return jsonify({
        'running': current_state['running'],
        'mode': current_state['mode'],
        'current_line': current_state['current_line'],
        'context_lines': list(current_state['context_lines']),
        'progress': current_state['progress'],
        'elapsed_seconds': elapsed_time,
        'completion_seconds': completion_time,
        'target_text': current_state['target_text'],
        'total_attempts': current_state['total_attempts'],
        'total_correct_chars': current_state['total_correct_chars'],
        'time_started': current_state['time_started'].isoformat() if current_state['time_started'] else None,
        'time_completed': current_state['time_completed'].isoformat() if current_state['time_completed'] else None,
        'last_update': current_state['last_update'].isoformat() if current_state['last_update'] else None,
        'is_completed': current_state['is_completed']
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
