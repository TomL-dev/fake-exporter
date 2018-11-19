FROM python:2.7.15-alpine3.8

WORKDIR /usr/app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["fake_exporter.py"]