from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from yunopyutils import build_logger

from . import crud, schemas, database
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
        return templates.TemplateResponse(
            "order_created.html",
            {"request": request, "order": db_order})
    except Exception as e:
        _LOGGER.info(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/orders", response_class=HTMLResponse)
async def list_orders(
    request: Request, 
    user_id: Optional[int] = Depends(get_user_id),
    db: AsyncSession = Depends(database.get_db)
):
    try:
        orders = await crud.get_orders(db, user_id)
        return templates.TemplateResponse(
            "list_orders.html",
            {"request": request, "orders": orders, "user_id": user_id})
    except Exception as e:
        _LOGGER.info(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

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