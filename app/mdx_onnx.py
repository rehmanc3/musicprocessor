from __future__ import annotations
import onnxruntime as ort
import numpy as np
from typing import Optional

class MDXSeparator:
    def __init__(self, model_path: str, providers: Optional[list[str]] = None, overlap: float = 0.25, frame_len: int = 44100*5):
        self.model_path = model_path
        self.session = ort.InferenceSession(model_path, providers=providers or ort.get_available_providers())
        self.overlap = overlap
        self.frame_len = frame_len
        # Infer IO names
        self.in_name = self.session.get_inputs()[0].name
        self.out_name = self.session.get_outputs()[0].name

    def _chunks(self, x: np.ndarray) -> list[np.ndarray]:
        # x: [2, T]
        hop = int(self.frame_len * (1 - self.overlap))
        frames = []
        for start in range(0, x.shape[-1], hop):
            end = min(start + self.frame_len, x.shape[-1])
            pad = self.frame_len - (end - start)
            chunk = x[:, start:end]
            if pad > 0:
                chunk = np.pad(chunk, ((0,0),(0,pad)))
            frames.append((start, end, pad, chunk))
            if end == x.shape[-1]:
                break
        return frames

    def separate(self, mix: np.ndarray, sr: int = 44100) -> np.ndarray:
        # mix: [2, T] float32 in [-1, 1]
        mix = np.ascontiguousarray(mix)
        out = np.zeros_like(mix)
        weight = np.zeros((1, mix.shape[-1]), dtype=np.float32)

        window = np.hanning(self.frame_len).astype(np.float32)
        window = np.clip(window, 1e-4, None)

        for (start, end, pad, chunk) in self._chunks(mix):
            inp = np.expand_dims(chunk, 0)  # [1, 2, L]
            pred = self.session.run([self.out_name], {self.in_name: inp})[0]  # [1,2,L]
            pred = np.squeeze(pred, 0)
            if pad > 0:
                pred = pred[:, :pred.shape[-1]-pad]
                win = window[:pred.shape[-1]]
            else:
                win = window
            out[:, start:start+pred.shape[-1]] += pred * win
            weight[:, start:start+pred.shape[-1]] += win

        out /= np.maximum(weight, 1e-4)
        return out.astype(np.float32)