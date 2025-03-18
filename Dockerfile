FROM python:3.10-alpine

RUN apk add --no-cache gcc musl-dev libpq-dev

WORKDIR /app

COPY requirement.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirement.txt

COPY src/ src/

ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
