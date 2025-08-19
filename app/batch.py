from __future__ import annotations
import os
import glob
from pathlib import Path
import numpy as np
from tqdm import tqdm
from .audio import load_audio, save_audio
from .mdx_onnx import MDXSeparator

SUPPORTED = (".wav", ".mp3", ".flac", ".ogg", ".m4a")


def run_batch(input_dir: str, output_dir: str, model_path: str, device: str = "cpu", overlap: float = 0.25, frame_len: int = 220500):
    os.makedirs(output_dir, exist_ok=True)
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if device == "cuda" else ["CPUExecutionProvider"]
    sep = MDXSeparator(model_path=model_path, providers=providers, overlap=overlap, frame_len=frame_len)

    files = [p for ext in SUPPORTED for p in glob.glob(os.path.join(input_dir, f"**/*{ext}"), recursive=True)]
    if not files:
        raise SystemExit("No audio files found.")

    for f in tqdm(files, desc="Separating", unit="file"):
        mix = load_audio(f)
        vocals = sep.separate(mix)
        # Optional: Create accompaniment by subtraction if the models estimates vocals
        accomp = mix - vocals
        stem_dir = Path(output_dir) / Path(f).stem
        stem_dir.mkdir(parents=True, exist_ok=True)
        save_audio(str(stem_dir / "vocals.wav"), vocals)
        save_audio(str(stem_dir / "accompaniment.wav"), accomp)