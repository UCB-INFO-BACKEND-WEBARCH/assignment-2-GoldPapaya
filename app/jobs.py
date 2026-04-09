from datetime import datetime, timedelta
import time
from redis import Redis
from rq import Queue
from .models import Task

redis_client = Redis.from_url('redis://redis:6379/0')
task_queue = Queue('tasks', connection=redis_client)
def schedule_task_notification(task_id, due_date):
    now = datetime.utcnow()
    if due_date is None or due_date <= now or due_date > now+timedelta(days=1):
        return False

    task_queue.enqueue('app.jobs.send_due_date_notification', task_id)
    return True

def send_due_date_notification(task_id):
    from . import app

    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return

        time.sleep(5) # explicitly added 5s wait to simulate the process taking time
        due = task.due_date.isoformat() if task.due_date else 'unknown'
        print(f"Reminder: Task '{task.title}' is due soon!")
