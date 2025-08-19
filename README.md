# MusicProcessor: Batch UVR-Style Source Separation

- Batch-separate large folders of songs into `vocals.wav` and `accompaniment.wav`
- ONNX Runtime with CUDA/CPU; Dockerized for reproducibility

## Quick Start (Docker)
docker compose run --rm isolator

## CLI (Python)
python -m app.batch /path/to/inputs /path/to/outputs /path/to/model.onnx --device cuda --overlap 0.5 --frame-len 220500

## Models
Place .onnx under ./models and pass via --model or MODEL_PATH.

## Tips
- GPU: set `--device cuda` (requires CUDAExecutionProvider)
- Quality vs speed: increase `--overlap` or `--frame-len` for quality; reduce for speed.
