FROM python:3.8

RUN apt-get -qqy update && \
        apt-get install -qqy \
        build-essential \
        gdal-bin \
        libgdal-dev \
        nano

EXPOSE 8005
ENV PYTHONUNBUFFERED 1

RUN mkdir /code

ADD requirements.txt /code/
ADD manage.py /code/
WORKDIR /code
RUN pip install -r requirements.txt

ADD onlinesoccermanager /code/onlinesoccermanager
ADD league /code/league
ADD oscsettings /code/oscsettings
ADD users /code/users

ADD entrypoint.sh /code/

CMD ["./entrypoint.sh", "daphne", "-b", "0.0.0.0", "-p", "8005", "onlinesoccermanager.asgi:application"]
