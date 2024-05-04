from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.database import engine, Base
from app.tables import couriers, orders

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Включение роутеров для обработки запросов
app.include_router(couriers.router)
app.include_router(orders.router)

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("<a href=""/docs"" target=""_blank"">Перейти на базу Яндекс Доставки</a>")
