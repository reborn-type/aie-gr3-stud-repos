FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY configs ./configs

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "docker_entrypoint.py"]
