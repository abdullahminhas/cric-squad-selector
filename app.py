import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cric.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager(app)
login_manager.login_view = "login"

from models import db, User  # noqa: E402
db.init_app(app)

from auth import auth as auth_blueprint  # noqa: E402
from squad_api import squad_bp  # noqa: E402
import ml_utils  # noqa: E402 - triggers model and data loading on startup

app.register_blueprint(auth_blueprint)
app.register_blueprint(squad_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/player-dashboard")
def player_dashboard():
    return render_template("player_dashboard.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
