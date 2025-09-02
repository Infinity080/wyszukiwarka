FROM python:3.12-slim 

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN apt-get update && apt-get install -y curl

COPY src/ /app/
COPY data/ /app/data/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]