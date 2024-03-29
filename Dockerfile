FROM python:3.9
COPY requirements.txt /
RUN pip install -r /requirements.txt
WORKDIR /app
COPY app /app
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app --access-logfile -
