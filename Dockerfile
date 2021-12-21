FROM python:3.8

COPY src/. /usr/src/nostradamus/
WORKDIR /usr/src/nostradamus
COPY requirements.txt .

RUN \
 python3 -m pip install --upgrade pip && \
 python3 -m pip install -r requirements.txt --user --no-cache-dir && \
 rm requirements.txt

EXPOSE 9345
CMD ["python", "nostradamus.py"]
