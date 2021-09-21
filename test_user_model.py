"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from re import U
from unittest import TestCase

from models import db, User, Message, Follows

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
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""



    def setUp(self):
        """Create test client, add sample data."""

     

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        


        db.session.add(u)
        db.session.commit()
        db.session.add(u2)
        db.session.commit()


    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.filter_by(username='testuser').first()
        u2 = u = User.query.filter_by(username='testuser2').first()


        # User should have no messages & no followers & no followings 
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)

       

    
    def test_user_is_following(self):
        # User should be able to add followers and be found 

        u = User.query.filter_by(username='testuser').first()
        u2 = u = User.query.filter_by(username='testuser2').first()


        self.assertFalse(u.is_following(u2))

        u.following.append(u2)

        self.assertTrue(u.is_following(u2))
        
        
    def test_user_is_followed_by(self):
        """ User should be able to detect who is following
        them and check if someone is not"""

        u = User.query.filter_by(username='testuser').first()
        u2 = u = User.query.filter_by(username='testuser2').first()
        self.assertFalse(u2.is_followed_by(u))

        u.following.append(u2)
        db.session.commit()
        self.assertTrue(u2.is_followed_by(u))

    def test_user_signup(self):
        new_user = User.signup(username= "newest", email = "testemail@test.com", password="livelaughlove", image_url="https://www.thoughtco.com/thmb/CcGtsWzKtmaeYCGrr5EEnK41T5A=/3863x2173/smart/filters:no_upscale()/close-up-view-of-a-mother-brown-bear-standing-over-her-cub-as-they-appear-to-be-looking-out-for-any-danger--kuril-lake--kamchatka--russia--827261734-5b97dfaa46e0fb0050b348af.jpg")

        self.assertNotEqual(new_user.password,"livelaughlove")
        self.assertEqual(new_user.username, "newest")
        self.assertEqual(new_user.email, "testemail@test.com")
        
        # User.signup should return a type error when entered incorectly 
        with self.assertRaises(TypeError):
            User.signup(username="nookay")



    def test_authenticate(self):
        u3 = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD3",
            image_url="none"
        )
        db.session.add(u3)
        db.session.commit()
        
        auth = User.authenticate(username="testuser3", password="HASHED_PASSWORD3")
        self.assertEqual(auth,u3)
        
        # testing to ensure that a mismatched password doesn't work and returns false
        auth2 = User.authenticate(username="testuser3", password="no match")
        self.assertFalse(auth2)

        # testing to ensure that a mismatched username doesn't work and returns false
        auth3 = User.authenticate(username="nousername", password="HASHED_PASSWORD3")
        self.assertFalse(auth3)