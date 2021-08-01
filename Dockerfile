FROM python:3
WORKDIR /app

RUN apt-get update

COPY . /app/

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN pip install discord.py
RUN pip install sqlalchemy
RUN pip install pyyaml


CMD ["python", "main.py"]