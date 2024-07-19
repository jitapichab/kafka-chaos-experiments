from typing import Optional, List
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from yunopyutils import build_logger

from . import crud, schemas, database,  kafka_producer,  models
from .dependencies import get_user_id

_LOGGER = build_logger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/create_order", response_class=HTMLResponse)
async def create_order_form(request: Request):
    return templates.TemplateResponse("create_order.html", {"request": request})


@router.post("/create_order", response_class=HTMLResponse)
async def create_order(
    request: Request,
    user_id: int = Form(...),
    pokemon: str = Form(...),
    country: str = Form(...),
    price: float = Form(...),
    db: AsyncSession = Depends(database.get_db)
):
    try:
        order = schemas.PokeOrderCreate(user_id=user_id,
                                        pokemon=pokemon,
                                        country=country,
                                        price=price)
        db_order = await crud.create_order(db, order)
        order_data = schemas.PokeOrder.from_orm(db_order).dict()
        kafka_producer.produce_order_message(order_data)
        return templates.TemplateResponse(
            "order_created.html",
            {"request": request, "order": db_order})
    except Exception as e:
        _LOGGER.info(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/list_orders", response_class=HTMLResponse)
async def list_orders(
    request: Request,
    state: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, gt=0),
    db: AsyncSession = Depends(database.get_db)
):
    try:
        # Convert state string to OrderState enum if it's a valid state
        state_filter = (
            models.OrderState(state)
            if state in models.OrderState.__members__ else None
        )
        orders = await crud.get_orders(db, state=state_filter,
                                       skip=skip, limit=limit)
        return templates.TemplateResponse(
            "list_orders.html",
            {
                "request": request,
                "orders": orders,
                "selected_state": state,
                "skip": skip,
                "limit": limit
            })
    except Exception as e:
        _LOGGER.info(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/orders/", response_model=schemas.PokeOrder)
async def new_order(order: schemas.PokeOrderCreate,
                    db: AsyncSession = Depends(database.get_db)):
    db_order = await crud.create_order(db, order)
    order_data = schemas.PokeOrder.from_orm(db_order).dict()
    kafka_producer.produce_order_message(order_data)
    return db_order


@router.get("/orders/", response_model=List[schemas.PokeOrder])
async def read_orders(state: Optional[str] = Query(None),
                      skip: int = Query(0, ge=0),
                      limit: int = Query(20, gt=0),
                      db: AsyncSession = Depends(database.get_db)):
    orders = await crud.get_orders(db, state=state,
                                   skip=skip, limit=limit)
    return orders

@router.get("/orders/{order_id}", response_model=schemas.PokeOrder)
async def get_order_by_id(order_id: int,
                          db: AsyncSession = Depends(database.get_db)):
    order = await crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}", response_model=schemas.PokeOrder)
async def update_order_state(
    order_id: int,
    state: schemas.PokeOrderUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    order = await crud.update_order_state(db, order_id, state.state)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.delete("/orders", response_class=HTMLResponse)
async def delete_all_orders(db: AsyncSession = Depends(database.get_db)):
    await crud.delete_all_orders(db)
    return {"detail": "All orders deleted"}