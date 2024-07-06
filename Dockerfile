FROM python:latest
MAINTAINER bvt2202
WORKDIR /home
RUN mkdir src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip3 install --no-cache --upgrade pip setuptools

COPY JobParserBackend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY JobParserBackend/src /home/src
COPY JobParserBackend/private_key.pem ./
COPY JobParserBackend/public_key.pem ./

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]

