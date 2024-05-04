from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import POSTGRES_DATABASE_URL
from app.database import db_manager
from app.tables import couriers, orders

db_manager.init(POSTGRES_DATABASE_URL)

app = FastAPI()

app.include_router(couriers.router)
app.include_router(orders.router)


@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("<a href=""/docs"" target=""_blank"">Перейти на базу Яндекс Доставки</a>")
