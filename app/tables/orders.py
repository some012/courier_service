import random
from datetime import datetime, timedelta
from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Order, Courier, OrderBackup
from app.utilities.default_response import DefaultResponse
from app.schemas.orders import CreateOrders, GetOrdersNotFinish, GetOrdersFinish

router = APIRouter(
    prefix="/api",
    tags=["orders"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/order", response_model=Union[List[GetOrdersNotFinish]], status_code=status.HTTP_200_OK)
def read_not_completed_orders(db: Session = Depends(get_db)):
    result = db.execute(select(Order))
    all_couriers = result.unique().scalars().all()
    return all_couriers


@router.get("/orders/{id}", response_model=Union[DefaultResponse, GetOrdersNotFinish, GetOrdersFinish],
            responses=responses)
def get_order(id: int, response: Response, db: Session = Depends(get_db)):
    order = db.execute(select(Order).filter(Order.id == id))
    this_order = order.scalar_one_or_none()  # также по id ищем заказ

    if this_order is None:  # если не нашли - ищем в бэкапе
        order = db.execute(select(OrderBackup).filter(OrderBackup.id == id))
        this_order = order.scalar_one_or_none()  # также по id ищем заказ
        return {
            "id": this_order.id,
            "courier_id": this_order.courier_id,
            "status": this_order.status,
            "district": this_order.district,
            "date_get": this_order.date_get,
            "date_end": this_order.date_end
        }

    return {
        "id": this_order.id,
        "courier_id": this_order.courier_id,
        "status": this_order.status,
        "district": this_order.district,
        "date_get": this_order.date_get
    }


@router.post("/orders", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
def create_order(response: Response, order_data: CreateOrders, db: Session = Depends(get_db)):
    courier = db.execute(  # смотрим у какого курьера нет сейчас активного заказа
        select(Courier).filter((Courier.active_order == None), Courier.districts.contains(order_data.district)))
    this_courier = courier.scalar_one_or_none()

    if this_courier is None:  # не нашли - выводим ошибку
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Courier not found")

    new_order = Order(  # нашли курьера, значит придаем ему этот заказ и
        # создаем его через CreateOrder, беря оттуда name и district
        name=order_data.name,
        district=order_data.district,
        date_get=datetime.now(),
        courier_id=this_courier.id,
        status=1)

    db.add(new_order)
    db.commit()

    return DefaultResponse(success=True, message="Order created successfully")


@router.post('/order/{id}', status_code=status.HTTP_201_CREATED)
def complete_order(id: int, db: Session = Depends(get_db)):
    order = db.execute(select(Order).filter(Order.id == id))  # находим заказ
    order_data = order.scalar_one_or_none()

    if not order_data:  # не нашли, так и не нашли
        return DefaultResponse(success=False, status_code=404, message="Order not found")
    if order_data.status == 2:  # случай, если пингуем уже завершенный заказ
        return DefaultResponse(success=True, status_code=201, message="Order completed")

    courier = db.execute(select(Courier).filter(
        (Courier.id == order_data.courier_id)))  # находим курьера, привязанного к требуемому заказу
    this_courier = courier.scalar_one_or_none()

    if this_courier:
        this_courier.active_order = []  # убираем активный заказ у курьера
        order_data.date_end = datetime.now() + timedelta(minutes=float(random.randrange(20, 60)))
        new_order = OrderBackup(  # создаем копию и отправляем в отдельную таблицу для статистики
            id=order_data.id,
            name=order_data.name,
            district=order_data.district,
            date_get=order_data.date_get,
            courier_id=order_data.courier_id,
            status=2,
            date_end=order_data.date_end)
        db.add(new_order)
        db.commit()

        return DefaultResponse(success=True, status_code=201, message="Order completed")
    else:
        return DefaultResponse(success=False, status_code=404, message="Courier not found for the order")


@router.delete("/order/{id}", response_model=DefaultResponse, responses=responses)
def remove_order(id: int, response: Response, db: Session = Depends(get_db)):
    order = db.execute(select(Order).filter(Order.id == id))  # находим заказ
    this_order = order.scalar_one_or_none()

    if this_order is None:  # заказ не нашли - ошибка
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Order not found")

    db.delete(this_order)  # нашли - сносим, тогда у курьеза привязанного к нему не будет активного заказа,
    db.commit()  # можно создать новый и он привяжется к нему, если район тот же

    return DefaultResponse(success=True, message="Order successfully removed")
