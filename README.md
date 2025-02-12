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

##
Check out the website: https://monkeytypewriter.pythonanywhere.com/
You can only view the current simulation running, the admin (me) can change/stop the simulation.
Anyone can view the stuff running though :)

## Simulation Modes

### Simple Mode
- Characters are randomly generated and accumulated when correct
- Incorrect characters are ignored

### Complex Mode
- Characters are randomly generated
- If an incorrect character is generated, the current line is reset
- More challenging than simple mode
