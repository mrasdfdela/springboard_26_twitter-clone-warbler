"""User model tests."""

# run these tests like:
#    python -m unittest test_message_model.py

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Likes, Follows
from test_helper import addUsers

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app

class MessageModelCreateTestCase(TestCase):
    """Test user models."""

    db.create_all()
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        self.client = app.test_client()

        addUsers()
        user1 = User.query.all()[0]
        user2 = User.query.all()[-1]

        new_msg = Message(
            text="Hello world!",
            user_id = user1.id
        )
        db.session.add(new_msg)
        db.session.commit()

        new_like = Likes(
            user_id = user2.id,
            message_id = new_msg.id
        )
        db.session.add(new_like)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does the basic user model work?"""
        user1 = User.query.all()[0]
        user2 = User.query.all()[-1]
        new_msg = Message.query.first()

        self.assertEqual(len(user1.messages),1)
        self.assertEqual(len(user2.messages),0)

        self.assertEqual(new_msg.text, "Hello world!")
        self.assertEqual(new_msg.user_id,user1.id)
        self.assertEqual(new_msg.user.username,user1.username)

    def test_message_likes(self):
        """Are message likes working correctly?"""
        user1 = User.query.all()[0]
        user2 = User.query.all()[-1]
        msg = Message.query.first()
        like = Likes.query.first()

        self.assertEqual(len(user1.likes),0)
        self.assertEqual(len(user2.likes),1)
        self.assertEqual(like.user_id,user2.id)
        self.assertNotEqual(like.user_id,msg.user.id)