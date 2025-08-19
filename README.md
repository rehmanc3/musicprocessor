# musicprocessor


[![CI](https://github.com/rehmanc3/musicprocessor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/<YOUR_GH_USERNAME>/musicprocessor/actions/workflows/ci.yml)

<!-- Container image (GHCR) – latest tag size & version -->
![GHCR Image Size](https://img.shields.io/docker/image-size/ghcr/rehmanc3/musicprocessor/latest)
![GHCR Version](https://img.shields.io/github/v/tag/rehmanc3/musicprocessor?label=ghcr%20tag)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<!-- Python & Platform -->
![Python](https://img.shields.io/badge/python-3.11-blue)
![OS](https://img.shields.io/badge/os-linux%20%7C%20macOS-informational)

<!-- Lint -->
[![ruff](https://img.shields.io/badge/lint-ruff-success)](https://github.com/astral-sh/ruff)

A **containerized, GPU-optional batch audio processing pipeline** (UVR-style source separation) built with ONNX Runtime.  
Designed for reproducible runs in local development, CI/CD, and Kubernetes environments.

---

## Features

- **Batch processing** of audio files (WAV/MP3/FLAC/OGG/M4A)
- **GPU/CPU runtime selection** (ONNX Runtime providers)
- **Containerized workflow** via Docker & docker-compose
- **CI/CD ready** with GitHub Actions (lint, test, build, publish to GHCR)
- **Kubernetes friendly** with example Job & Helm starter

---

## Quick Start

### CPU Run (Docker)

```bash
git clone https://github.com/rehmanc3/musicprocessor
cd musicprocessor

# Build image
docker build -t ghcr.io/rehmanc3/musicprocessor:dev .

# Prepare directories
mkdir -p inputs outputs models
# Place your ONNX model in ./models

# Run processing (CPU)
docker run --rm \
  -v $PWD/inputs:/workspace/inputs \
  -v $PWD/outputs:/workspace/outputs \
  -v $PWD/models:/workspace/models \
  ghcr.io/rehmanc3/musicprocessor:dev \
  python -m app.batch --inputs /workspace/inputs --outputs /workspace/outputs --model /workspace/models/model.onnx --device cpu --overlap 0.5
```

### GPU Run (Docker Compose)

```bash
# Requires NVIDIA Container Toolkit installed
docker compose --profile gpu up --build
```

---

## CLI Usage

```bash
python -m app.batch \
  --inputs </path/to/inputs> \
  --outputs </path/to/outputs> \
  --model </path/to/model.onnx> \
  --device [cpu|cuda] \
  --overlap 0.5 \
  --frame-len 220500
```

---

## Development

```bash
# Lint & type-check
ruff check .
mypy app

# Run unit tests
pytest -q
```

---

## Containers & Deployment

- **Images**: published to [GHCR](https://github.com/rehmanc3/musicprocessor/pkgs/container/musicprocessor)
- **docker compose**: profiles for CPU and GPU workloads
- **Kubernetes**: job manifest + Helm chart starter in `charts/musicprocessor`

---

## Configuration

Set environment variables in `.env` or pass via CLI:

- `MODEL_PATH` – path to ONNX model (default `/workspace/models/model.onnx`)
- `INPUT_DIR` – input audio directory (default `/workspace/inputs`)
- `OUTPUT_DIR` – output audio directory (default `/workspace/outputs`)
- `DEVICE` – `cpu` or `cuda`
- `OVERLAP` – overlap fraction (default `0.5`)

---

## License

MIT © [rehmanc3](https://github.com/rehmanc3)

---

## Angle

This project demonstrates:

- **Containerization** (multi-stage Docker builds, slim images)

- **CI/CD pipelines** (GitHub Actions → GHCR)

- **Automation** (batch jobs, GPU/CPU runtime handling)

- **Orchestration readiness** (docker-compose, Kubernetes Job, Helm chart)

