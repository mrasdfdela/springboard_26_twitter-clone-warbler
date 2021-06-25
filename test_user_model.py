"""User model tests."""

# run these tests like:
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows
from test_helper import addUsers

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app

class UserModelCreateTestCase(TestCase):
    """Test user models."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does the basic user model work?"""

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
        def valid_user():
            User.signup(
              username="valid_testuser",
              password="HASHED_PASSWORD",
              email="test@test.com",
              image_url=User.image_url.default.arg
            )
            db.session.commit()

        def invalid_user():
            User.signup(
              username="valid_testuser",
              password="CODED_PASSWORD",
              email="invalid_email",
              image_url=User.image_url.default.arg
            )

        valid_user()
        self.assertTrue(User.query.first().username == 'valid_testuser')

        with self.assertRaises(IntegrityError):
          invalid_user()
          db.session.commit()

    def test_user_model_authenticate(self):
        User.signup(
          username="testuser",
          password="HASHED_PASSWORD",
          email="test@test.com",
          image_url=User.image_url.default.arg
        )

        self.assertEqual(
          User.authenticate("testuser","HASHED_PASSWORD"),
          User.query.first()
        )

        self.assertFalse(User.authenticate("invalid_user","HASHED_PASSWORD"))

        self.assertFalse(User.authenticate("testuser","CODED_PASSWORD"))