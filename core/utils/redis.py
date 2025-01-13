from core.logger import LOGGER
from aioredis import Redis
from core.config.redis import REDIS_CONFIG
import json

redis_url = (
    f"redis://:{REDIS_CONFIG['password']}@{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}"
)
redis_client = Redis.from_url(redis_url)


async def publish_message(channel: str, message: dict):
    await redis_client.publish(channel, json.dumps(message))


async def subscribe_to_channel(channel: str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            return json.loads(message["data"].decode("utf-8"))
        