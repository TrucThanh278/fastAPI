FROM python:3.10-alpine

RUN apk add --no-cache gcc musl-dev libpq-dev

# Đặt thư mục làm việc
WORKDIR /app

COPY requirement.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirement.txt

COPY . .

ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
