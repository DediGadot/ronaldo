# Stage 1: Build the frontend
FROM node:18-alpine AS build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the backend
FROM python:3.12-slim
WORKDIR /app
COPY --from=build /app/frontend/dist /app/static
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
COPY create_tables.py .
RUN python create_tables.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
