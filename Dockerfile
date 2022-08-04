FROM nostradamusai/nostradamus:base

COPY src/. /usr/src/nostradamus/
WORKDIR /usr/src/nostradamus

EXPOSE 9345
CMD ["python", "nostradamus.py"]