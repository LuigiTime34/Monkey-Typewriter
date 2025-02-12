from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    admin = User(username='admin', password_hash=generate_password_hash('hinge255'))
    db.session.add(admin)
    db.session.commit()