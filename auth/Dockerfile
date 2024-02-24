FROM python:3.9

WORKDIR /app

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1


ENV PYTHONUNBUFFERED 1


RUN pip install  --upgrade pip 


RUN pip install -r requirements.txt




ENTRYPOINT  ["/app/entrypoint.sh"]

