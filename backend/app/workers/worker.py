import redis
from rq import Worker, Queue
from app.config import settings

redis_conn = redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn)
w = Worker([q])
w.work()
