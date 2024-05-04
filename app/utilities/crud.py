from sqlalchemy import func


def average_order_completion_time(db, model, model_courier):
    # Выбираем все заказы, у которых есть время завершения
    completed_orders = db.query(model).filter(model_courier.id == model.courier_id).all()

    total_completion_time = 0
    num_completed_orders = len(completed_orders)

    for order in completed_orders:
        completion_time = order.date_end - order.date_get
        total_completion_time += completion_time.total_seconds()

    if num_completed_orders > 0:
        # Преобразование общего времени выполнения в минуты
        average_completion_time_minutes = total_completion_time / (num_completed_orders * 60)
        return "{:.2f}".format(average_completion_time_minutes)
    else:
        return None


def average_order_days(db, model, model_courier):
    # Выбираем количество заказов за каждый день
    daily_order_count = db.query(func.count(model.id)) \
        .filter(model.courier_id == model_courier.id) \
        .group_by(func.date_trunc('day', model.date_end)) \
        .all()

    # Вычисляем среднее количество заказов в день
    total_orders = len(daily_order_count)
    total_order_count = sum(count for count, in daily_order_count)
    if total_orders > 0:
        average_orders_per_day = total_order_count / total_orders
        return int(average_orders_per_day)
    else:
        return None
