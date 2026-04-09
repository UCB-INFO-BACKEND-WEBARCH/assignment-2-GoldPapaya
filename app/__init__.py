from flask import Flask

from .models import db
from .routes.tasks import tasks_bp
from .routes.categories import categories_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/tasks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(tasks_bp)
app.register_blueprint(categories_bp)

# create db tables when flask app starts
with app.app_context():
    db.create_all()
