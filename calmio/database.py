from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    BooleanField,
    IntegerField,
    DateTimeField,
    TextField,
    ForeignKeyField,
    FloatField,
)
from datetime import datetime
from pathlib import Path
from platformdirs import user_data_dir
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Define the database connection
data_dir = Path(user_data_dir("Calmio"))
data_dir.mkdir(parents=True, exist_ok=True)
db_path = data_dir / "calmio.db"
db = SqliteDatabase(db_path)


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class BaseModel(Model):
    class Meta:
        database = db


class Setting(BaseModel):
    key = CharField(unique=True)
    value = JSONField()


class Session(BaseModel):
    start_time = DateTimeField()
    duration = IntegerField()
    breaths = IntegerField()
    last_inhale = FloatField()
    last_exhale = FloatField()
    cycles = JSONField(null=True)


class Badge(BaseModel):
    code = CharField(unique=True)
    count = IntegerField(default=0)


class DailyBadge(BaseModel):
    date = DateTimeField()
    badge = ForeignKeyField(Badge, backref="daily_entries")
    count = IntegerField(default=0)


class DailyChallenge(BaseModel):
    date = DateTimeField(unique=True)
    text = TextField()
    completed = BooleanField(default=False)


def initialize_database():
    """Create the database tables and run migrations."""
    with db:
        db.create_tables(
            [Setting, Session, Badge, DailyBadge, DailyChallenge], safe=True
        )
    log.info("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
