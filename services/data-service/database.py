from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance (to be bound with Flask app later)
db = SQLAlchemy()


class EventRecord(db.Model):
    """
    Database model representing an event record.

    This table stores event-related information such as
    title, description, location, status, and classification metadata.
    """
    __tablename__ = 'event_records'

    # Primary key: unique identifier for each record
    id = db.Column(db.Integer, primary_key=True)

    # Basic event information
    title = db.Column(db.String(100), nullable=False)  # Event title (required)
    description = db.Column(db.Text)  # Detailed event description
    location = db.Column(db.String(100))  # Event location
    date = db.Column(db.String(20))  # Event date (stored as string)

    # Organizer information
    organiser = db.Column(db.String(100))  # Name of event organiser

    # Status field (e.g., PENDING, APPROVED, REJECTED)
    status = db.Column(db.String(20), default="PENDING")

    # Classification fields (used for categorization and prioritization)
    category = db.Column(db.String(20))  # Event category
    priority = db.Column(db.String(20))  # Event priority level

    # Additional notes or remarks
    note = db.Column(db.String(200))