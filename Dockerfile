FROM python:3.9.1
LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

RUN pip install meinheld gunicorn

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY . /app
WORKDIR /app/

RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/start.sh"]