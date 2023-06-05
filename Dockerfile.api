FROM python:3.9

COPY ./src /app/src
COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt

WORKDIR /app/src

EXPOSE 3001

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=3001"]