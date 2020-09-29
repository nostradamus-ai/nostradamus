FROM python:3.7

COPY src/. /usr/src/nostradamus/
WORKDIR /usr/src/nostradamus
COPY requirements.txt .

RUN \
 pip3 install --upgrade pip && \
 pip3 install -r requirements.txt --no-cache-dir && \
 rm requirements.txt

EXPOSE 9345
CMD ["python", "nostradamus.py"]
