from models import db, User, Message, Follows

def addUsers():
    u1 = User(
        email="test@test.com",
        username="testuser",
        password="HASHED_PASSWORD")

    u2 = User(
    email="trial@trial.com",
    username="trialuser",
    password="CODED_PASSWORD")
    
    db.session.add_all([u1,u2])
    db.session.commit()