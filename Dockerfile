FROM python:3.12
RUN mkdir /fastapi_app
WORKDIR /fastapi_app
COPY req.txt .
RUN pip install --upgrade pip
RUN pip install -r req.txt
COPY . .
WORKDIR /fastapi_app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]
