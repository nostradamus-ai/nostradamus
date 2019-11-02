FROM python:3.7-alpine

RUN mkdir -p /usr/src/nostradamus
WORKDIR /usr/src/nostradamus
COPY src/* ./
COPY requirements.txt .

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install cython && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps && \
 rm requirements.txt

EXPOSE 9345
CMD ["python", "nostradamus.py"]
