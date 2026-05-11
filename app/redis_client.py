import redis.asyncio as redis
from config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True, ssl_cert_reqs=None)

async def get_redis():
    return redis_client