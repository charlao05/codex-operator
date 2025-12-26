FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

ENV PYTHONUNBUFFERED=1

# Default entrypoint: run CLI. Override at runtime if needed.
ENTRYPOINT ["python", "-m", "src.cli"]
