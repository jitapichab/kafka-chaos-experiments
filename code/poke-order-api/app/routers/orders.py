from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .. import schemas, crud, database, kafka_producer

router = APIRouter()


@router.post("/orders/", response_model=schemas.PokeOrder)
async def create_order(order: schemas.PokeOrderCreate, 
                       db: AsyncSession = Depends(database.get_db)):
    db_order = await crud.create_order(db, order)
    kafka_producer.produce_order_message(db_order.dict())
    return db_order


@router.get("/orders/", response_model=List[schemas.PokeOrder])
async def read_orders(user_id: Optional[int] = None, 
                      db: AsyncSession = Depends(database.get_db)):
    orders = await crud.get_orders(db, user_id)
    return orders