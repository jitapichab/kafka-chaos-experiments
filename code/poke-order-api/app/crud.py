from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, schemas


async def create_order(db: Session, order: schemas.PokeOrderCreate):
    db_order = models.PokeOrder(**order.dict(),
                                state=models.OrderState.pending)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_orders(db: Session,
                     state: models.OrderState = None,
                     skip: int = 0, limit: int = 10):
    query = select(models.PokeOrder)
    if state is not None:
        query = query.filter(models.PokeOrder.state == state)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_order_by_id(db: Session, order_id: int):
    return await db.get(models.PokeOrder, order_id)


async def update_order_state(db: Session, order_id: int,
                             state: schemas.OrderState):
    order = await db.get(models.PokeOrder, order_id)
    if order:
        order.state = state
        await db.commit()
        await db.refresh(order)
    return order


async def delete_all_orders(db: Session):
    await db.execute(text('DELETE FROM poke_orders'))
    await db.commit()
