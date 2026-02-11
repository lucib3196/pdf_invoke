from pathlib import Path
from typing import Iterable, List

import pymupdf

from pdf_invoke.types import ImageExt, PDFInput
from pdf_invoke.utils import get_image_type, is_pdf_bytes


class PDFImageConverter:
    def pdf_to_images(
        self, pdf: PDFInput, zoom: float = 0.2, ext: ImageExt = "png"
    ) -> List[bytes]:
        doc = None
        try:
            if isinstance(pdf, (bytes, bytearray, memoryview)):
                pdf_bytes = bytes(pdf)
                self._validate_pdf_bytes(pdf_bytes)
                doc = pymupdf.open(stream=pdf, filetype="pdf")

            elif isinstance(pdf, (Path, str)):
                doc = pymupdf.open(Path(pdf).as_posix())
            else:
                raise TypeError("PDF is not of expected type")
            assert doc
            pass
        except Exception as e:
            raise ValueError(f"Failed to open pdf {e}")

        matrix = pymupdf.Matrix(zoom, zoom)
        image_bytes = [page.get_pixmap(matrix=matrix).tobytes(ext) for page in doc]
        doc.close()
        return image_bytes

    def images_to_pdf(
        self, images: Iterable[bytes], allowed_formats=["png", "jpeg"]
    ) -> bytes:
        self._validate_image_bytes(images, allowed_formats)
        doc = pymupdf.open()
        for img_bytes in images:
            img_doc = pymupdf.open(stream=img_bytes, filetype=get_image_type(img_bytes))
            rect = img_doc[0].rect
            page = doc.new_page(width=rect.width, height=rect.height)
            page.insert_image(rect, stream=img_bytes)
            img_doc.close()
        pdf_bytes = doc.tobytes()
        # Should be bytes either way but just to make sure
        self._validate_pdf_bytes(pdf_bytes)
        doc.close()
        return pdf_bytes

    def _validate_pdf_bytes(self, data):
        if not is_pdf_bytes(data):
            raise ValueError("Document is not pdf")

    def _validate_image_bytes(
        self,
        images: Iterable[bytes],
        allowed_formats: set[str] | None = None,
    ) -> List[str]:
        formats = []
        for idx, img_bytes in enumerate(images):
            try:
                fmt = get_image_type(img_bytes)

                if allowed_formats and fmt.lower() not in allowed_formats:
                    raise ValueError(
                        f"Image at index {idx} has unsupported format: {fmt}"
                    )
                formats.append(fmt)
            except Exception as e:
                raise ValueError(f"Invalid image at index {idx}: {e}") from e
        return formats


if __name__ == "__main__":
    print("Test")
    path = Path(r"pdf_invoke\data\Lecture_02_03.pdf")
    image = Path(r"pdf_invoke\data\images\Lecture_02_03_page_1.png").read_bytes()
    print(image[:10])
    print(get_image_type(image))
