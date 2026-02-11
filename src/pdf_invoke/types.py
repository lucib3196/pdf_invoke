from pathlib import Path
from typing import Literal, Iterable


PDFInput = str | Path | bytes
ImageInput = str | Path | bytes
ImageBytes = bytes
ImageExt = Literal["png", "jpeg"]
ALLOWED_MIME = Literal["image/jpeg", "image/png"]
