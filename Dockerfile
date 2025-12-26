FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

ENV PYTHONUNBUFFERED=1

# Default command: show readiness message. Replace with your entrypoint when packaging.
CMD ["python", "-c", "print('codex-operator container ready')"]
