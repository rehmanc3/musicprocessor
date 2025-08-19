from pathlib import Path
from app.audio import save_audio, load_audio
import numpy as np

# Create a tiny stereo sine file and ensure I/O works
p = Path('tmp.wav')
sr = 44100
x = np.sin(2*np.pi*440*np.arange(sr)/sr).astype('float32')
x = np.stack([x, x])
save_audio(str(p), x, sr)
y = load_audio(str(p), sr)
assert y.shape[0] == 2 and y.dtype == np.float32