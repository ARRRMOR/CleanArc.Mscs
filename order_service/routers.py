from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemes import OrderDefault, ResponseOrder
from services import create_order_service, get_order_service
from database import get_db


router = APIRouter(prefix="/orders")

@router.post("/", response_model=ResponseOrder)
async def create_order(order: OrderDefault, db: AsyncSession = Depends(get_db)):
    return await create_order_service(order, db)

@router.get("/{order_id}", response_model=ResponseOrder)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_order_service(order_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="ORDER NOT FOUND")
    return result
