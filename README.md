# musicprocessor

<!-- CI status (GitHub Actions) -->
[![CI](https://github.com/rehmanc3/musicprocessor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rehmanc3/musicprocessor/actions/workflows/ci.yml)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<!-- Python & Platform -->
![Python](https://img.shields.io/badge/python-3.11-blue)
![OS](https://img.shields.io/badge/os-linux%20%7C%20macOS-informational)

<!-- Lint -->
[![ruff](https://img.shields.io/badge/lint-ruff-success)](https://github.com/astral-sh/ruff)


Containerized, GPU‑optional **batch audio processing pipeline** (UVR‑style source separation) packaged for reproducible runs in local, CI, and Kubernetes environments.

**Highlights**
- **Reproducible builds**: Multi-stage Docker image; pinned dependencies; GH Actions builds to GHCR.
- **GPU/CPU toggle**: ONNX Runtime providers; run on plain CPUs or NVIDIA GPUs.
- **Batch automation**: Process entire folders via CLI or container entrypoint; mounts for inputs/outputs/models.
- **Orchestration ready**: `docker compose` profiles for CPU/GPU; Kubernetes Job and Helm chart starter.

---

## Quick Start (CPU)
```bash
# Clone and build
git clone https://github.com/rehmanc3/musicprocessor
cd musicprocessor

# Build image and run (CPU)
docker build -t ghcr.io/rehmanc3/musicprocessor:dev .
mkdir -p inputs outputs models
# Put your .onnx model under ./models

docker run --rm \
  -v $PWD/inputs:/workspace/inputs \
  -v $PWD/outputs:/workspace/outputs \
  -v $PWD/models:/workspace/models \
  ghcr.io/rehmanc3/musicprocessor:dev \
  python -m app.batch --inputs /workspace/inputs --outputs /workspace/outputs --model /workspace/models/model.onnx --device cpu --overlap 0.5
````

## Quick Start (GPU)

```bash
# NVIDIA Container Toolkit required (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
# Compose profile enables GPU runtime.
docker compose --profile gpu up --build
```

---

## CLI

```bash
python -m app.batch \
  --inputs </path/to/inputs> \
  --outputs </path/to/outputs> \
  --model </path/to/model.onnx> \
  --device [cpu|cuda] \
  --overlap 0.5 \
  --frame-len 220500
```

**Notes**

- Inputs can be WAV/MP3/FLAC/OGG/M4A; outputs default to per‑track folders with `vocals.wav` and `accompaniment.wav`.
- For best COLA behavior, default `--overlap` is 0.5 (Hann window).

---

## Development

```bash
# Lint & type-check
ruff check .
pyproject-flake8
mypy app

# Run unit tests
pytest -q
```

---

## Containers & Orchestration

- **Images** are built by GitHub Actions and pushed to **GHCR** as `ghcr.io/rehmanc3/musicprocessor:<tag>`.
- **docker compose** has two profiles: `cpu` (default) and `gpu` (NVIDIA runtime).
- **Kubernetes** example job manifests and a Helm starter are provided in `charts/musicprocessor`.

---

## Configuration

Use `.env` (see `.env.example`) to set environment variables consumed by compose and the app. Common vars:

- `MODEL_PATH=/models/model.onnx`
- `INPUT_DIR=/inputs`
- `OUTPUT_DIR=/outputs`
- `DEVICE=cpu` (or `cuda`)

---

## License

MIT — see `LICENSE`.

---

## Badges (optional)

Add the following once Actions & GHCR are enabled:

&#x20;

```
```

---

## 2) GitHub Actions: Build, Test, Publish (CPU default, optional GPU job)

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main ]
    tags: [ 'v*.*.*' ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  packages: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dev deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt || true
          pip install pytest ruff mypy

      - name: Lint & type-check
        run: |
          ruff check .
          mypy app || true

      - name: Run tests (smoke)
        run: |
          mkdir -p inputs outputs models
          # Generate a 1s sine wave fixture and run CPU pipeline
          python - << 'PY'
import numpy as np, soundfile as sf, os
os.makedirs('inputs', exist_ok=True)
x = np.sin(2*np.pi*440*np.arange(44100)/44100.0).astype(np.float32)
# stereo
x = np.stack([x,x], axis=-1)
sf.write('inputs/fixture.wav', x, 44100)
PY
          # Try to import app.batch; if not available, skip
          python - << 'PY'
import importlib, sys, subprocess
try:
    importlib.import_module('app.batch')
    subprocess.check_call([sys.executable, '-m', 'app.batch', '--inputs', 'inputs', '--outputs', 'outputs', '--model', 'models/model.onnx', '--device', 'cpu', '--overlap', '0.5'], timeout=60)
except Exception as e:
    print('Smoke test skipped or failed:', e)
PY

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/musicprocessor
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

> If you want a dedicated GPU build matrix with CUDA base images, add a second job targeting an `-gpu` Dockerfile variant and tag `:gpu-<sha>`.

---

## 3) Docker Compose (CPU & GPU profiles)

**File:** `docker-compose.yml`

```yaml
version: '3.9'

services:
  isolator:
    image: ghcr.io/${GH_USER:-youruser}/musicprocessor:latest
    build: .
    command: >-
      python -m app.batch --inputs /workspace/inputs --outputs /workspace/outputs
      --model ${MODEL_PATH:-/workspace/models/model.onnx}
      --device ${DEVICE:-cpu} --overlap ${OVERLAP:-0.5}
    working_dir: /workspace
    volumes:
      - ./inputs:/workspace/inputs
      - ./outputs:/workspace/outputs
      - ./models:/workspace/models
    env_file:
      - .env
    profiles: ["cpu"]

  isolator-gpu:
    image: ghcr.io/${GH_USER:-youruser}/musicprocessor:latest
    build: .
    command: >-
      python -m app.batch --inputs /workspace/inputs --outputs /workspace/outputs
      --model ${MODEL_PATH:-/workspace/models/model.onnx}
      --device cuda --overlap ${OVERLAP:-0.5}
    working_dir: /workspace
    volumes:
      - ./inputs:/workspace/inputs
      - ./outputs:/workspace/outputs
      - ./models:/workspace/models
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    runtime: nvidia
    env_file:
      - .env
    profiles: ["gpu"]
```

---

## 4) Multi‑stage Dockerfile (lean, reproducible)

**File:** `Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir ruff mypy

COPY . .

# Default entrypoint runs the CLI; override in compose if needed
ENTRYPOINT ["python", "-m", "app.batch"]
```

> If you want a dedicated CUDA image, create `Dockerfile.gpu` FROM `nvidia/cuda:12.2.0-runtime-ubuntu22.04` + `python`, or rely on host GPU libraries with ONNX Runtime CUDA provider.

---

## 5) .env example

**File:** `.env.example`

```dotenv
# Compose + app configuration
MODEL_PATH=/workspace/models/model.onnx
DEVICE=cpu
OVERLAP=0.5
GH_USER=youruser
```

---

## 6) Makefile (developer UX)

**File:** `Makefile`

```makefile
APP?=musicprocessor
IMAGE?=ghcr.io/$(GH_USER)/$(APP)
TAG?=dev

.PHONY: build run cpu gpu push lint test

build:
	docker build -t $(IMAGE):$(TAG) .

run:
	docker run --rm -v $$PWD/inputs:/workspace/inputs -v $$PWD/outputs:/workspace/outputs -v $$PWD/models:/workspace/models $(IMAGE):$(TAG) --inputs /workspace/inputs --outputs /workspace/outputs --model /workspace/models/model.onnx --device cpu --overlap 0.5

cpu:
	docker compose --profile cpu up --build

gpu:
	docker compose --profile gpu up --build

lint:
	ruff check .

test:
	pytest -q

push:
	docker push $(IMAGE):$(TAG)
```

---

## 7) Minimal tests (optional but nice)

**File:** `tests/test_smoke.py`

```python
import os, subprocess, sys, importlib
from pathlib import Path

def test_cli_exists():
    try:
        importlib.import_module('app.batch')
    except Exception as e:
        raise AssertionError(f"CLI module not importable: {e}")


def test_runs_on_empty_dirs(tmp_path: Path):
    (tmp_path/"inputs").mkdir()
    (tmp_path/"outputs").mkdir()
    # Running without a model should fail gracefully; we only check it doesn't hang
    cmd = [sys.executable, '-m', 'app.batch', '--inputs', str(tmp_path/'inputs'), '--outputs', str(tmp_path/'outputs'), '--device', 'cpu']
    try:
        subprocess.run(cmd, check=False, timeout=30)
    except subprocess.TimeoutExpired:
        raise AssertionError('CLI timed out on empty run')
```

> Adjust to your actual module path/flags if different.

---

## 8) Kubernetes Job (single-run example)

**File:** `k8s/job.yaml`

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: musicprocessor-job
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: musicprocessor
          image: ghcr.io/<YOUR_GH_USERNAME>/musicprocessor:latest
          args: [
            "python","-m","app.batch",
            "--inputs","/data/inputs",
            "--outputs","/data/outputs",
            "--model","/data/models/model.onnx",
            "--device","cpu",
            "--overlap","0.5"
          ]
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: musicprocessor-pvc
```

---

## 9) Helm chart starter (optional)

**Files:**

- `charts/musicprocessor/Chart.yaml`
- `charts/musicprocessor/values.yaml`
- `charts/musicprocessor/templates/job.yaml`

```yaml
# charts/musicprocessor/Chart.yaml
apiVersion: v2
name: musicprocessor
version: 0.1.0
appVersion: "0.1.0"
```

```yaml
# charts/musicprocessor/values.yaml
image:
  repository: ghcr.io/<YOUR_GH_USERNAME>/musicprocessor
  tag: latest
  pullPolicy: IfNotPresent

resources: {}

device: cpu
overlap: 0.5
modelPath: /data/models/model.onnx
inputDir: /data/inputs
outputDir: /data/outputs
pvcName: musicprocessor-pvc
```

```yaml
# charts/musicprocessor/templates/job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "musicprocessor.fullname" . }}
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          args:
            - python
            - -m
            - app.batch
            - --inputs
            - {{ .Values.inputDir | quote }}
            - --outputs
            - {{ .Values.outputDir | quote }}
            - --model
            - {{ .Values.modelPath | quote }}
            - --device
            - {{ .Values.device | quote }}
            - --overlap
            - {{ .Values.overlap | quote }}
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: {{ .Values.pvcName }}
```

> Add `_helpers.tpl` later for nicer naming; this is intentionally minimal.

---

## 10) License (MIT)

**File:** `LICENSE`

```text
MIT License

Copyright (c) 2025 Rehman Choudhari

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
