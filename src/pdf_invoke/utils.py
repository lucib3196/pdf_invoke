from PIL import Image
import io
from typing import Iterable, List


def is_pdf_bytes(data: bytes) -> bool:
    return data.startswith(b"%PDF-")


def get_image_type(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            assert img.format
            return img.format  # e.g., 'PNG', 'JPEG'
    except Exception:
        raise ValueError("Provided bytes are not a valid image.")


def validate_image_bytes(
    images: Iterable[bytes],
    allowed_formats: set[str] | None = None,
) -> List[str]:
    formats = []
    for idx, img_bytes in enumerate(images):
        try:
            fmt = get_image_type(img_bytes)

            if allowed_formats and fmt.lower() not in allowed_formats:
                raise ValueError(f"Image at index {idx} has unsupported format: {fmt}")
            formats.append(fmt)
        except Exception as e:
            raise ValueError(f"Invalid image at index {idx}: {e}") from e
    return formats
