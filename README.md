# Infinite Monkey Theorem Simulator

A Flask-based web application that simulates the infinite monkey theorem by randomly generating characters to match a target text. The application includes user authentication, real-time simulation tracking, and multiple simulation modes.

## Features

- Real-time character generation simulation
- Two simulation modes: simple and complex
- User authentication system
- Progress tracking and statistics
- RESTful API endpoints
- Persistent storage using SQLite
- Context-aware display of recently matched lines

## Requirements

- Python 3.x
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Werkzeug

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LuigiTime34/Monkey-Typewriter
cd Money-Typewriter
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python app.py
```
or
```bash
python3 app.py
```

## Configuration

- `SECRET_KEY`: Set your secret key in the app configuration
- `SQLALCHEMY_DATABASE_URI`: Configure your database path (default: 'sqlite:///monkey.db')
- Template directory is automatically configured relative to the script location

## Usage

1. Start the application:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

3. Log in using admin credentials

4. Start a new simulation:
   - Enter target text
   - Select simulation mode (simple/complex)
   - Click "Start"

## API Endpoints

### Authentication Required

- `POST /api/start`
  - Starts a new simulation
  - Parameters:
    - `text`: Target text to simulate
    - `mode`: Simulation mode ("simple" or "complex")

- `POST /api/stop`
  - Stops the current simulation

### Public Endpoints

- `GET /api/status`
  - Returns current simulation status including:
    - Running state
    - Current progress
    - Statistics
    - Timing information

## Simulation Modes

### Simple Mode
- Characters are randomly generated and accumulated when correct
- Incorrect characters are ignored

### Complex Mode
- Characters are randomly generated
- If an incorrect character is generated, the current line is reset
- More challenging than simple mode

## Database Models

### User
- Stores user authentication information
- Fields:
  - `id`: Primary key
  - `username`: Unique username
  - `password_hash`: Hashed password

### SimulationState
- Stores simulation history
- Fields:
  - `id`: Primary key
  - `target_text`: The text being simulated
  - `current_progress`: Current simulation progress
  - `timestamp`: When the simulation was created

## Security Features

- Password hashing using Werkzeug security
- Flask-Login integration for session management
- Protected admin routes
- CSRF protection via Flask-WTF (ensure SECRET_KEY is set)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]