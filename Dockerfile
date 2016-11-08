FROM python:3-alpine

MAINTAINER strahe <u@strahe.com>

ADD ddns.py ddns.py

ENTRYPOINT ["python", "ddns.py"]
