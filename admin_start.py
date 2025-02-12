from models import db, User
from werkzeug.security import generate_password_hash
from app import app

with app.app_context():
    db.create_all()
    admin = User(username='admin', password_hash=generate_password_hash('ha you thought I was going to share my password'))
    db.session.add(admin)
    db.session.commit()