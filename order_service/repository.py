from sqlalchemy.ext.asyncio import AsyncSession
from schemes import OrderDefault, ResponseOrder
from models import Order
import logging
import json
import os
import redis.asyncio as aioredis
import aio_pika
import asyncio
from redis_manager import get_redis


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBIT_MQ_URL = os.getenv("RABBITMQ_URL", "amqp://shkibidi1:pokazal1@rabbitmq:5672/")


QUEUE_NAME = "order_queue"

connection = None
channel = None

async def connection_to_rabbitmq():
    global connection, channel
    while connection is None:
        try:
            connection = await aio_pika.connect_robust(RABBIT_MQ_URL)
            channel = await connection.channel()
            logger.info(f"✅ Connected to RabbitMQ: {connection}")
        except Exception as e:
            logger.info(f"🔄 Waiting for RabbitMQ... {e}, connection: {connection}")
            await asyncio.sleep(5)  # Подождать перед новой попыткой

async def send_to_rabbitmq(queue_name, message: dict) -> None:
    """Отправляет сообщение в очередь, используя переиспользуемое подключение."""
    global channel
    if channel is None:  # Проверяем, есть ли активный канал
        await connection_to_rabbitmq()

    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(message).encode("utf-8")),  # Сообщение
        routing_key=queue_name,  # Отправляем в очередь
    )


async def create_order(order: OrderDefault, db: AsyncSession) -> Order:
    db_order = Order(items=[item.model_dump() for item in order.items], user_id=order.user_id)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    order_dict = db_order.to_dict()
    # Отправляем в RabbitMQ
    await send_to_rabbitmq(QUEUE_NAME, {"status": "new", "info": order_dict})

    return db_order


async def get_order(order_id: int, db: AsyncSession) -> Order | None:
    """Получаем заказ из кэша Redis или базы данных."""
    redis_client = await get_redis()
    if redis_client is None:
        logger.error("❌ Redis client is not initialized!")
        raise RuntimeError("Redis client is not connected")

    # Сначала проверим кэш Redis
    cached_order = await redis_client.get(f"order:{order_id}")
    if cached_order:
        logger.info(f"✅ Found order in Redis cache: {order_id}")
        order_data = json.loads(cached_order)
        # Преобразуем items обратно в список объектов Items
        return Order(**order_data)

    # Если не найдено в Redis, ищем в базе данных
    result = await db.get(Order, order_id)
    if result:
        # Преобразуем ORM объект в Pydantic модель (OrderDefault)
        result_dict = ResponseOrder.model_validate(result.to_dict())  # Преобразуем в Pydantic модель

        # Сериализуем в JSON и сохраняем в Redis
        await redis_client.set(f"order:{order_id}", result_dict.model_dump_json(), ex=300)
        logger.info(f"✅ Found order in database and cached it: {order_id}")

        # Возвращаем ORM объект (сохраненный в базе)
        return result

    logger.warning(f"❌ Order not found: {order_id}")
    return None



async def main():
    await connection_to_rabbitmq()  # Подключение при старте













