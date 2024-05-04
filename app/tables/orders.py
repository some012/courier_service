from typing import Union

from fastapi import APIRouter, status, Response, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Order, Courier
from app.schemas.default_response import DefaultResponse
from app.schemas.orders import CreateOrders, GetOrders

router = APIRouter(
    prefix="/api",
    tags=["orders"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/orders/{id}", response_model=Union[GetOrders, DefaultResponse], responses=responses)
async def get_order(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    order = await db.execute(select(Order).filter(Order.id == id))
    this_order = order.scalar_one_or_none()  # также по id ищем заказ

    if this_order is None:  # если не нашли - выводим ошибку
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Order not found")

    return this_order


@router.post("/orders", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
async def create_order(response: Response, order_data: CreateOrders, db: AsyncSession = Depends(get_db)):
    courier = await db.execute(  # смотрим у какого курьера нет сейчас активного заказа
        select(Courier).filter((Courier.active_order == None), Courier.districts.contains(order_data.district)))
    this_courier = courier.scalar_one_or_none()

    if this_courier is None:  # не нашли - выводим ошибку
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Courier not found")

    new_order = Order(  # нашли курьера, значит придаем ему этот заказ и
        # создаем его через CreateCourier, беря оттуда name и district
        name=order_data.name,
        district=order_data.district,
        courier_id=this_courier.id,
        status=1)

    db.add(new_order)
    await db.commit()

    return DefaultResponse(success=True, message="Order created successfully")


@router.post('/order/{id}', status_code=status.HTTP_201_CREATED)
async def complete_order(id: int, db: AsyncSession = Depends(get_db)):
    order = await db.execute(select(Order).filter(Order.id == id))  # находим заказ
    order_data = order.scalar_one_or_none()

    if not order_data:  # не нашли, так и не нашли
        return DefaultResponse(success=False, status_code=404, message="Order not found")
    if order_data.status == 2:  # случай, если пингуем уже завершенный заказ
        return DefaultResponse(success=True, status_code=201, message="Order completed")

    courier = await db.execute(select(Courier).filter(
        (Courier.id == order_data.courier_id)))  # находим курьера, привязанного к требуемому заказа
    this_courier = courier.scalar_one_or_none()

    if this_courier:
        order_data.status = 2  # завершаем заказ
        await db.commit()

        return DefaultResponse(success=True, status_code=201, message="Order completed")
    else:
        return DefaultResponse(success=False, status_code=404, message="Courier not found for the order")


@router.delete("/order/{id}", response_model=DefaultResponse, responses=responses)
async def remove_courier(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    order = await db.execute(select(Order).filter(Order.id == id))  # находим заказ
    this_order = order.scalar_one_or_none()

    if this_order is None:  # заказ не нашли - ошибка
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Order not found")

    await db.delete(this_order)  # нашли - сносим, тогда у курьеза привязанного к нему не будет активного заказа,
    await db.commit()            # можно создать новый и он привяжется к нему, если район тот же

    return DefaultResponse(success=True, message="Order successfully removed")