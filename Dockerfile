FROM python:3.10-slim

ARG AWS_RDS_URL
ENV AWS_RDS_URL ${AWS_RDS_URL}

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./app /src/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
