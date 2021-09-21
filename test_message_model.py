from datetime import time
import os
from re import U
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
    """tests the Message model"""

    @classmethod
    def setUpClass(cls):

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
    
    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def setUp(self):
        """Create test client, add sample data."""
        
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        m = Message(
            text = "testing text",
            user_id = 1
        )

    def Test_Message_create(self):
        m = Message.query.filter(Message.text == "testing text").first()
        self.assertEqual(m.text, "testing text")
        self.assertEqual(type(m.user_id), type(1))
        