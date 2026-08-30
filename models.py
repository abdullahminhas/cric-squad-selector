import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    squads        = db.relationship("SavedSquad", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class SavedSquad(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    label       = db.Column(db.String(120), nullable=False)   # e.g. "Australia vs India – T20"
    format      = db.Column(db.String(20), nullable=False)
    team        = db.Column(db.String(80), nullable=False)
    opposition  = db.Column(db.String(80), nullable=False)
    players_json = db.Column(db.Text, nullable=False)         # JSON list of player dicts
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def players(self):
        return json.loads(self.players_json)

    def to_dict(self):
        return {
            "id":         self.id,
            "label":      self.label,
            "format":     self.format,
            "team":       self.team,
            "opposition": self.opposition,
            "players":    self.players,
            "created_at": self.created_at.strftime("%d %b %Y, %I:%M %p"),
        }

    def __repr__(self):
        return f"<SavedSquad {self.label}>"
