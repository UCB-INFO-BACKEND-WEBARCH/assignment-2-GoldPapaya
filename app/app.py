from flask import Flask
from redis import Redis
from rq import Queue
from datetime import datetime
import os

from .models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI',
    'postgresql://postgres:postgres@postgres:5432/tasks'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Redis connection
redis_client = Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
task_queue = Queue('tasks', connection=redis_client)

