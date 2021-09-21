"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

from csv import DictReader
import os
from unittest import TestCase

from sqlalchemy.sql.elements import Null

from models import db, connect_db, Message, User, Follows

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

    @classmethod
    def setUpClass(cls):

        db.drop_all()
        db.create_all()

        with open('generator/users.csv') as users:
            db.session.bulk_insert_mappings(User, DictReader(users))

        with open('generator/messages.csv') as messages:
            db.session.bulk_insert_mappings(Message, DictReader(messages))

        with open('generator/follows.csv') as follows:
            db.session.bulk_insert_mappings(Follows, DictReader(follows))

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.add(testuser)
        db.session.commit()

    def setUp(self):
        """Create test client, add sample data."""

        self.testuser = User.query.filter(User.username == "testuser").first()

        self.client = app.test_client()




    def test_home_route(self):
        """ test home route when sign out"""
        with self.client as c:
            
            resp_test_1 = c.get('/')
            html_1 = resp_test_1.get_data(as_text = True)

            self.assertEqual(resp_test_1.status_code, 200)

            self.assertIn("Sign up now to get your own personalized timeline",html_1)
    
    def test_home_route_signed_in(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp_test_1 = c.get('/')
            html_1 = resp_test_1.get_data(as_text = True)

            self.assertEqual(resp_test_1.status_code, 200)
            self.assertIn('<li><a href="/logout">Log out</a></li>',html_1)

    def test_sign_up(self):
        with self.client as c:
            resp = c.get('/signup')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<input class="form-control" id="username" name="username"',html)
            self.assertIn('id="email"',html)
            self.assertIn('Sign me up!',html)

    def test_users_page_route(self):
        with self.client as c:
            resp = c.get('/users/1')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)

    def test_users_followers_page_route(self):
        with self.client as c:
            resp = c.get('/users/1/followers',follow_redirects=True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Redirect (302)',html)
            # print(html)
            self.assertIn('<a href="/">/</a>',html)

    def test_users_followers_page_route_signedin(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/users/1/followers')
            html = resp.get_data(as_text = True)

            print(html)
            self.assertEqual(resp.status_code, 200)
            # self.assertIn('Maybe key community young ahead.',html)



    def test_add_message_signedin(self):
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
            self.assertEqual(resp.status_code, 200)

            msg = Message.query.filter(Message.user_id == self.testuser.id).first()
            self.assertEqual(msg.text, "Hello")
            db.session.delete(msg)
            db.session.commit()

    def test_add_message(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "this should not work!!"},follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text = True)

            msg = Message.query.filter(Message.user_id == self.testuser.id).first()
            self.assertIn("Redirect (302)", html)
        
            self.assertEqual(msg, None)

    def test_delete_message_logedin(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp_1 = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp_1.status_code, 200)
            msg = Message.query.filter(Message.user_id == self.testuser.id).first()

            self.assertEqual(msg.text, "Hello")

            resp_2 = c.post(f"/messages/{msg.id}/delete")
            self.assertEqual(resp_2.status_code, 200)
            html_2 = resp_2.get_data(as_text = True)

            msg = Message.query.filter(Message.user_id == self.testuser.id).first()
            self.assertEqual(msg, None)

    def test_delete_message(self):
        msg = Message(text="this should not be deleted")
        self.testuser.messages.append(msg)
        db.session.commit()
        
        with self.client as c:
            # print(msg.id)
            resp = c.post(f"/messages/{msg.id}/delete")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text = True)
            
            self.assertIn('<a href="/">/</a>',html)

            msg = Message.query.filter(Message.user_id == self.testuser.id).first()
            self.assertEqual(msg.text, "this should not be deleted")

        db.session.delete(msg)
        db.session.commit()


    def test_delete_message_other_user(self):
        msg = Message.query.get(1)


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
        self.assertNotEqual(msg.user_id, self.testuser.id)

        resp= c.post("/messages/1/delete")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text = True)
        
        self.assertIn('a href="/">/</a>',html)

        msg_1 = Message.query.get(1)
        self.assertEqual(msg.text, msg_1.text)
