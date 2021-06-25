"""Message View tests."""

# run these tests like:
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        # User.query.delete()
        # Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.otheruser = User.signup(
                                    username="otheruser",
                                    email="other@test.com",
                                    password="otheruser",
                                    image_url=None)
        db.session.commit()

        self.otherfollow = Follows(
            user_being_followed_id = self.testuser.id,
            user_following_id = self.otheruser.id
        )

        self.testmsg = Message(
            text = "Hello world!",
            user_id = self.testuser.id
        )
        db.session.add(self.otherfollow)
        db.session.add(self.testmsg)
        db.session.commit()
        db.session.expire_on_commit=False

    def test_list_users(self):
        """View all users"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<img src="/static/images/default-pic.png" alt="{self.testuser.username}">', html)
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)
            self.assertIn('<p class="card-bio">', html)

            """Logout and view"""            
            c.get('/logout',follow_redirects=True)
            new_resp = c.get("/users")
            html = new_resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a href="/login">Log in</a>', html)
            self.assertIn('<p class="card-bio">', html)

    
    def test_user(self):
        """View user profile"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>Hello world!</p>',html)

            """Logout and view profile"""
            c.get('/logout')
            new_resp = c.get(f"/users/{self.testuser.id}")
            html = new_resp.get_data(as_text=True)

            self.assertEqual(new_resp.status_code, 200)
            self.assertIn('<p>Hello world!</p>',html)
            self.assertIn('<a href="/login">Log in</a>', html)
            self.assertNotIn('<button class="btn btn-primary">Unfollow</button>', html)

    def test_user_followers(self):
        """View user followers"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>@otheruser</p>',html)

            """Logout and view followers -> access denied"""
            c.get('/logout')
            new_resp = c.get(f"/users/{self.testuser.id}/followers",follow_redirects=True)
            html = new_resp.get_data(as_text=True)

            self.assertEqual(new_resp.status_code, 200)
            self.assertIn('Access unauthorized',html)

    def test_user_follow_other(self):
        """Follow & Unfollow other user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/follow/2",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>@otheruser</p>',html)
            self.assertIn('<button class="btn btn-primary btn-sm">Unfollow</button>',html)
          
            """Unfollow"""
            resp = c.post(f"/users/stop-following/2", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<p>@otheruser</p>',html)
            self.assertNotIn('<button class="btn btn-primary btn-sm">Unfollow</button>',html)

            """Logout and follow/unfollow -> access denied"""
            c.get('/logout')
            follow_resp = c.post(f"/users/follow/2",follow_redirects=True)
            html = follow_resp.get_data(as_text=True)
            self.assertIn('Access unauthorized',html)

            unfollow_resp = c.post("/users/stop-following/2",follow_redirects=True)
            html = unfollow_resp.get_data(as_text=True)
            self.assertIn('Access unauthorized',html)


    def test_edit_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.otheruser.id
            resp = c.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertTrue(resp.status_code,200)
            self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>',html)

            new_resp = c.post("/users/profile", data = dict(username='testuser',email='test@test.com',password='testuser',image_url=None,bio='dont know much biology'),follow_redirects=True)
            new_html = new_resp.get_data(as_text=True)

            self.assertTrue(resp.status_code, 200)
            self.assertIn('<p>dont know much biology</p>',new_html)

            """Logout and edit -> access denied"""
            c.get('/logout')
            new_resp = c.get(f"/users/profile",follow_redirects=True)
            html = new_resp.get_data(as_text=True)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>',html)

    def test_delete_user(self):
        """Delete current user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.otheruser.id
            resp = c.post("/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertTrue(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>',html)

            all_users = [ user.username for user in User.query.all() ]
            self.assertFalse(self.otheruser.username in all_users)

            """Logout and delete user -> access denied"""
            c.get('/logout')
            follow_resp = c.post(f"/users/delete",follow_redirects=True)
            html = follow_resp.get_data(as_text=True)
            self.assertIn('Access unauthorized',html)