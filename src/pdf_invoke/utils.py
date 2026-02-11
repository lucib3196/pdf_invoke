from PIL import Image
import io


def is_pdf_bytes(data: bytes) -> bool:
    return data.startswith(b"%PDF-")


def get_image_type(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            assert img.format
            return img.format  # e.g., 'PNG', 'JPEG'
    except Exception:
        raise ValueError("Provided bytes are not a valid image.")
