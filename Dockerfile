FROM python:3

MAINTAINER J. Christopher Bare

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["/app/start.sh"]
CMD ["run"]
