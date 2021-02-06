FROM python:3

RUN pip3 install requests
COPY rest.py /rest.py
COPY .apikeys /.apikeys

ENTRYPOINT ["python3", "rest.py"]

