"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from test_helper import addUsers

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelCreateTestCase(TestCase):
    """Test user models."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""
        addUsers()

        user = User.query.first()

        # User should have no messages & no followers
        self.assertEqual(len(user.messages), 0)
        self.assertEqual(len(user.followers), 0)
        self.assertEqual(f"{user}", f'<User #{user.id}: {user.username}, {user.email}>')
    
    def test_user_model_follows(self):
        """Does following work?"""
        addUsers()
        
        user1 = User.query.first()
        user2 = User.query.all()[-1]

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True)
        self.assertEqual(user2.is_following(user1), False)        
        self.assertEqual(user1.is_followed_by(user2), False)
        self.assertEqual(user2.is_followed_by(user1), True)
    
    def test_user_model_create(self):
        """Does the signup function work?"""
        valid_credentials = {"testuser","test@test.com","HASHED_PASSWORD","/static/images/default-pic.png"}
        invalid_credentials = {"testuser","CODED_PASSWORD","trial@trial.com","/static/images/default-pic.png"}

        import pdb
        pdb.set_trace()
        User.signup(*valid_credentials)

        # def signup(credentials):
        #     u = User.signup(*credentials)
        #     db.session.commit()
        # self.assertRaises(ValueError,signup(valid_credentials))
        # self.assertRaises(ValueError,signup(valid_credentials))
        # import pdb
        # pdb.set_trace()