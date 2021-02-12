FROM python:3

WORKDIR /mnt/mydata/
RUN pip3 install requests
COPY rest.py /rest.py
COPY .apikeys /.apikeys


ENTRYPOINT ["python3", "rest.py"]
