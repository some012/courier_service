FROM python:3.12
RUN mkdir /fastapi_app
WORKDIR /fastapi_app
COPY req.txt .
RUN pip install --upgrade pip
RUN pip install -r req.txt
COPY . .
WORKDIR /fastapi_app

CMD gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:9000
