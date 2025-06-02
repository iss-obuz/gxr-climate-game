__all__ = ["cube", "event", "game"]

from pathlib import Path
import os

ROOT = Path(__file__).absolute().parent.parent
DATA = ROOT / "data"
PNG = ROOT / "png"
if not os.path.exists(DATA):
    os.makedirs(DATA)
if not os.path.exists(PNG):
    os.makedirs(PNG)
