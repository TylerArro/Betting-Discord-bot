FROM python:3.10

ADD bot.py .

RUN pip install -U py-cord pandas numpy

CMD ["python", "./bot.py"]