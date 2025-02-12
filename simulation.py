from models import db, SimulationState
from datetime import datetime
import random
import time
import threading

class ContinuousSimulation:
    def __init__(self):
        self.running = False
        self.current_text = ''
        self.current_line = ''
        self.line_number = 0
        self.mode = 'simple'
        self.total_attempts = 0
        self.total_correct_chars = 0
        self.time_started = None
        self.time_completed = None
        self.context_lines = []
        
    def generate_random_char(self):
        return chr(random.randint(32, 126))
        
    def run_simulation(self, app):
        with app.app_context():
            self.time_started = datetime.utcnow()
            while self.running:
                if not self.current_text:
                    time.sleep(1)
                    continue
                    
                lines = self.current_text.splitlines()
                if self.line_number >= len(lines):
                    # Save final state and stop
                    self.time_completed = datetime.utcnow()
                    state = SimulationState(
                        target_text=self.current_text,
                        current_progress=f"Completed: {self.total_correct_chars} chars, {self.total_attempts} attempts",
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(state)
                    db.session.commit()
                    self.running = False
                    break
                    
                target_line = lines[self.line_number]
                current_pos = len(self.current_line)
                
                if current_pos >= len(target_line):
                    # Save progress periodically
                    state = SimulationState(
                        target_text=self.current_text,
                        current_progress=f"Line {self.line_number}: {self.current_line}",
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(state)
                    db.session.commit()
                    
                    if len(self.context_lines) >= 3:
                        self.context_lines.pop(0)
                    self.context_lines.append(self.current_line)
                    self.current_line = ''
                    self.line_number += 1
                    continue
                    
                target_char = target_line[current_pos]
                random_char = self.generate_random_char() if target_char != '\n' else '\n'
                
                self.total_attempts += 1
                if random_char == target_char:
                    self.current_line += random_char
                    self.total_correct_chars += 1
                elif self.mode == 'complex':
                    self.current_line = ''
                    
                time.sleep(0.01)  # Prevent overwhelming the server
                
    def start(self, text, mode='simple'):
        from app import app  # Import app here to avoid circular import
        
        self.current_text = text
        self.mode = mode
        self.line_number = 0
        self.current_line = ''
        self.total_attempts = 0
        self.total_correct_chars = 0
        self.time_started = None
        self.time_completed = None
        self.context_lines = []
        
        if not self.running:
            self.running = True
            threading.Thread(target=self.run_simulation, args=(app,), daemon=True).start()
            
    def stop(self):
        self.running = False
        self.time_completed = datetime.utcnow()

# Create a global simulation instance
continuous_sim = ContinuousSimulation()