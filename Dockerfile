FROM python:3.7

RUN mkdir -p /usr/src/nostradamus
WORKDIR /usr/src/nostradamus
COPY src/* ./
COPY requirements.txt .

RUN \
 pip3 install --upgrade pip && \
 pip3 install -r requirements.txt --no-cache-dir && \
 rm requirements.txt

EXPOSE 9345
CMD ["python", "nostradamus.py"]