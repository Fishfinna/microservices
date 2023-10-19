FROM ubuntu:18.04
LABEL maintainer="shanti.steingagnon@gmail.com"

RUN apt-get update -y &&\
    apt-get install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY ./proccessing/* /app

ENTRYPOINT ["python3"]
CMD ["app.py"]