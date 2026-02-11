from pathlib import Path
from typing import Literal


PDFInput = str | Path | bytes
ImageBytes = bytes
ImageExt = Literal["png", "jpeg"]
ALLOWED_MIME = Literal["image/jpeg", "image/png"]
