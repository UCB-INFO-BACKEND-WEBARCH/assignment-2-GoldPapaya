from redis import Redis
from rq import Worker, Queue, Connection
from app.jobs import redis_client

listen = ['tasks']
if __name__ == '__main__': # runs when python worker.py is called
    connection = Redis.from_url('redis://redis:6379/0')
    with Connection(connection):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
