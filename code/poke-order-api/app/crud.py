from sqlalchemy.future import select
from sqlalchemy.orm import Session
from . import models, schemas


async def create_order(db: Session, order: schemas.PokeOrderCreate):
    db_order = models.PokeOrder(**order.dict(),
                                state=models.OrderState.pending)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_orders(db: Session, user_id: int = None):
    if user_id is not None:
        result = await db.execute(
            select(models.PokeOrder).filter(
                models.PokeOrder.user_id == user_id)
            )
    else:
        result = await db.execute(select(models.PokeOrder))
    return result.scalars().all()


async def update_order_state(db: Session, order_id: int,
                             state: schemas.OrderState):
    order = await db.get(models.PokeOrder, order_id)
    if order:
        order.state = state
        await db.commit()
        await db.refresh(order)
    return order


async def delete_all_orders(db: Session):
    await db.execute('DELETE FROM poke_orders')
    await db.commit()
