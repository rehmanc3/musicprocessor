FROM python:3.11-slim

# System deps for audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY models ./models
COPY tests ./tests

# Default to CLI batch entrypoint (GUI is for local use)
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "app.batch"]