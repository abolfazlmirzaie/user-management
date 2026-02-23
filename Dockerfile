FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

COPY entrypoint.sh /app/entrypoint.sh


RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]