from pathlib import Path
from typing import Literal
from enum import Enum

PDFInput = str | Path | bytes
ImageBytes = bytes
ImageExt = Literal["png", "jpeg"]