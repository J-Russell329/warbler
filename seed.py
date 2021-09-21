"""Seed database with sample data from CSV Files."""
from app import *

app = Flask(__name__)
uri = os.environ.get("DATABASE_URL", 'postgresql:///warbler')  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
if uri == "postgresql:///warbler":
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

    app.config['SQLALCHEMY_ECHO'] = True


print(uri)


from csv import DictReader
from app import db
from models import User, Message, Follows

connect_db(app)
db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))

db.session.commit()
