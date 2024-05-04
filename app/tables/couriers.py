import random
from datetime import datetime
from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.models import Courier, Order
from app.schemas.courier import CreateCourier, GetAllCourier, \
    GetWithoutOrderCourier, GetWithOrderCourier
from app.schemas.default_response import DefaultResponse

router = APIRouter(
    prefix="/api",
    tags=["courier"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/courier", response_model=Union[List[GetAllCourier]],
            status_code=status.HTTP_200_OK)  # вывод всех курьеров
async def read_couriers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Courier))
    all_couriers = result.unique().scalars().all()
    return all_couriers


@router.get("/courier/{id}", response_model=Union[GetWithoutOrderCourier, GetWithOrderCourier],
            responses=responses)  # вывод определенного курьера
async def get_courier(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    courier = await db.execute(select(Courier).filter(Courier.id == id))  # находим курьера
    this_courier = courier.scalar_one_or_none()
    if this_courier is None:  # если не нашли такой же id - выводим ошибку, что курьера не нашли
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Courier not found")

    active_order = await db.execute(select(Order).filter(this_courier.id == Order.courier_id))
    this_active_order = active_order.scalar_one_or_none()  # находим заказ курьера через courier_id

    if this_active_order is None:  # если не нашли, выводим avg_order_complete_time и avg_day_orders
        return {
            "id": this_courier.id,
            "name": this_courier.name,
            "avg_order_complete_time": this_courier.avg_order_complete_time,
            "avg_day_orders": this_courier.avg_day_orders
        }
    else:  # если все-таки нашли - показываем информацию активного заказа

        active_order1 = {
            "id": this_active_order.id,
            "name": this_active_order.name,
            "courier_id": this_active_order.courier_id,
            "district": this_active_order.district,
            "status": this_active_order.status
        }
        # возвращаем вместе с небольшой информацией о курьере
        return {
            "id": this_courier.id,
            "name": this_courier.name,
            "active_order": active_order1
        }


@router.post("/courier", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
async def create_courier(courier_data: CreateCourier, db: AsyncSession = Depends(get_db)):
    districts_str = ', '.join(courier_data.districts)  # превращаем в строку для адекватного вывода

    new_courier = Courier(  # через CreateCourier создаем нового курьера, беря оттуда name и districts
        name=courier_data.name,
        districts=districts_str,
        avg_order_complete_time=datetime.now(),
        avg_day_orders=random.randint(0, 20))

    db.add(new_courier)
    await db.commit()

    return DefaultResponse(success=True, message="Courier created successfully")


@router.delete("/courier/{id}", response_model=DefaultResponse, responses=responses)
async def remove_courier(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    courier = await db.execute(select(Courier).filter(Courier.id == id))  # находим курьера
    this_courier = courier.scalar_one_or_none()

    if this_courier is None:  # если не нашли такой же id - выводим ошибку, что курьера не нашли
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Courier not found")

    await db.delete(this_courier)  # удаляем
    await db.commit()

    return DefaultResponse(success=True, message="Courier successfully removed")
