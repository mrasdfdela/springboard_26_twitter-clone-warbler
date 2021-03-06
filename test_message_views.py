"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

            """Logout and add message -> access denied"""            
            c.get('/logout')
            new_resp = c.get("/messages/new",follow_redirects=True)
            html = new_resp.get_data(as_text=True)
            self.assertEqual(new_resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

            post_resp = c.post("/messages/new", follow_redirects=True)
            html = post_resp.get_data(as_text=True)
            self.assertIn('Access unauthorized', html)

    def test_add_message_redirect(self):
        """Will new adding a message redirect?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>Hello</p>", html)
      
    def test_show_message(self):
        """Will showing a message work correctly?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()
            resp = c.get(f"/messages/{msg.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<p class="single-message">{msg.text}</p>', html)

            """Logout and show message"""            
            c.get('/logout')
            new_resp = c.get(f"/messages/{msg.id}")
            html = new_resp.get_data(as_text=True)
            self.assertEqual(new_resp.status_code, 200)
            self.assertIn('<p class="single-message">', html)
            self.assertIn('<a href="/login">Log in</a>', html)

    def test_delete_message(self):
        """Will deleting a message work correctly?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(len(Message.query.all()), 0)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h4 id="sidebar-username">@{self.testuser.username}</h4>', html)

            """Logout and delete message -> access denied"""            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()

            c.get('/logout')
            new_resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = new_resp.get_data(as_text=True)
            self.assertEqual(new_resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            self.assertEqual(len(Message.query.all()),1)