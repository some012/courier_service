from typing import Union, List

from fastapi import APIRouter, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import OrderBackup
from app.schemas.order_backup import Orders_Backup
from app.utilities.default_response import DefaultResponse

router = APIRouter(
    prefix="/api",
    tags=["orders_backup"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/order_backup", response_model=Union[List[Orders_Backup]], status_code=status.HTTP_200_OK)
def read_completed_orders(db: Session = Depends(get_db)):
    result = db.execute(select(OrderBackup))
    all_couriers = result.unique().scalars().all()
    return all_couriers


@router.delete("/order_backup/{id}", response_model=DefaultResponse, responses=responses)
def remove_order(id: int, response: Response, db: Session = Depends(get_db)):
    order = db.execute(select(OrderBackup).filter(OrderBackup.id == id))  # находим заказ
    this_order = order.scalar_one_or_none()

    if this_order is None:  # заказ не нашли - ошибка
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Order not found")

    db.delete(this_order)  # нашли - сносим, тогда у курьеза привязанного к нему не будет активного заказа,
    db.commit()  # можно создать новый и он привяжется к нему, если район тот же

    return DefaultResponse(success=True, message="Order successfully removed")
