from pathlib import Path
from typing import Iterable, List

import pymupdf

from pdf_invoke.types import ImageExt, PDFInput
from pdf_invoke.utils import get_image_type, is_pdf_bytes, validate_image_bytes


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
        validate_image_bytes(images, allowed_formats)
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

    def save_pdf_to_images(
        self,
        pdf: PDFInput,
        output_path: str | Path,
        pdf_name: str | None = None,
        ext: ImageExt = "png",
        start: int = 0,
    ) -> str:
        pdf_name = self._validate_pdf_name(pdf, pdf_name)
        output_path = self._validate_path(output_path)
        data = self.pdf_to_images(pdf)
        for i, b in enumerate(data, start=start):
            out = output_path / f"{pdf_name}_page_{i}.{ext}"
            out.write_bytes(b)
        return output_path.as_posix()

    def save_images_to_pdf(
        self,
        images: Iterable[bytes],
        output_path: str | Path,
        pdf_name: str,
    ) -> str:
        pdf_name = self._validate_pdf_name(name=pdf_name)
        output_path = self._validate_path(output_path)
        pdf_path = output_path / pdf_name

        if pdf_path.suffix.lower() != ".png":
            pdf_path = pdf_path.with_suffix(".png")

        pdf_bytes = self.images_to_pdf(images)

        pdf_path.write_bytes(pdf_bytes)
        return pdf_path.as_posix()

    def _validate_pdf_name(
        self,
        pdf: PDFInput | None = None,
        name: str | None = None,
    ) -> str:

        if isinstance(pdf, (str, Path)):
            return Path(pdf).stem

        if name is not None:
            return name

        raise ValueError(
            "Unable to determine PDF name. "
            "Provide either a file path (str or Path) or explicitly pass `name` "
            "when supplying raw PDF bytes."
        )

    def _validate_pdf_bytes(self, data):
        if not is_pdf_bytes(data):
            raise ValueError("Document is not pdf")

    def _validate_path(self, path: str | Path) -> Path:
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Failed to validate pdf {path} cannot be resolved")
        return path


if __name__ == "__main__":
    print("Test")
    path = Path(r"pdf_invoke\data\Lecture_02_03.pdf")
    image = Path(r"pdf_invoke\data\images\Lecture_02_03_page_1.png").read_bytes()
    print(image[:10])
    print(get_image_type(image))
