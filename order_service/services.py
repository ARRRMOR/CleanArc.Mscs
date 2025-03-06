from sqlalchemy.ext.asyncio import AsyncSession
from repository import create_order, get_order
from schemes import OrderDefault, ResponseOrder

async def create_order_service(order: OrderDefault, db: AsyncSession) -> ResponseOrder:
    result = await create_order(order, db)
    return ResponseOrder.model_validate(result)


async def get_order_service(order_id: int, db: AsyncSession) -> ResponseOrder | None:
    result = await get_order(order_id, db)
    return ResponseOrder.model_validate(result) if result else None
