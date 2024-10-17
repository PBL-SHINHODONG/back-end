FROM python:3.10-slim

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./app /src/app

COPY ./.env /src/.env

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
