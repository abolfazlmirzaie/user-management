FROM python:3.11

WORKDIR /app

COPY riquirementes.txt /app/
RUN pip install -r riquirementes.txt

COPY . /app/

COPY entrypoint.sh /app/


RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]