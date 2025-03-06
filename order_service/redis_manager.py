import redis.asyncio as aioredis
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_client = None  # Глобальный клиент

async def connect_to_redis():
    """ Создаёт подключение к Redis при старте. """
    global redis_client
    redis_client = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        await redis_client.ping()
        logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")

async def close_redis():
    """ Закрывает соединение при завершении работы сервиса. """
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("🔌 Redis connection closed")

async def get_redis():
    if not redis_client:
        raise RuntimeError("Redis клиент не подключен")
    return redis_client
