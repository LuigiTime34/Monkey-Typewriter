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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monkey.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global variables to store simulation state
current_state = {
    'running': False,
    'current_line': '',
    'context_lines': deque(maxlen=3),
    'target_text': '',
    'progress': {'line': 0, 'total_lines': 0},
    'time_started': None,
    'last_update': None
}

# Database Models
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
        
        if random_char == target_char:
            current_state['current_line'] += random_char
            
        current_state['last_update'] = datetime.utcnow()
        time.sleep(0.01)  # Prevent overwhelming the system

# Routes
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
    
    if not target_text:
        return jsonify({'error': 'No text provided'}), 400
        
    current_state['target_text'] = target_text
    current_state['progress'] = {'line': 0, 'total_lines': len(target_text.splitlines())}
    current_state['current_line'] = ''
    current_state['context_lines'].clear()
    current_state['time_started'] = datetime.utcnow()
    
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
    return jsonify({
        'running': current_state['running'],
        'current_line': current_state['current_line'],
        'context_lines': list(current_state['context_lines']),
        'progress': current_state['progress'],
        'time_started': current_state['time_started'].isoformat() if current_state['time_started'] else None,
        'last_update': current_state['last_update'].isoformat() if current_state['last_update'] else None
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
