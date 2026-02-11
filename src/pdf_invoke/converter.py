from pathlib import Path
from typing import Iterable, List

import pymupdf

from pdf_invoke.types import ImageExt, PDFInput
from pdf_invoke.utils import get_image_type, is_pdf_bytes, validate_image_bytes


class PDFImageArchiver:
    """
    Utility class for converting between PDF documents and image byte streams,
    as well as persisting those conversions to disk.

    Responsibilities:
    ---------------
    - Convert a PDF (path or bytes) into a list of image bytes.
    - Convert a sequence of image bytes into a single PDF byte stream.
    - Save PDF pages as individual image files.
    - Save image bytes as a PDF file.
    - Perform internal validation for PDF bytes and file paths.

    Notes:
    ------
    - Uses PyMuPDF (pymupdf) for rendering and document manipulation.
    - Accepts both raw byte inputs and filesystem paths.
    - Does not manage directory creation — output paths must already exist.
    - Validation helpers assume `is_pdf_bytes`, `validate_image_bytes`,
      and `get_image_type` are defined elsewhere.
    """

    def pdf_to_images(
        self, pdf: PDFInput, zoom: float = 0.2, ext: ImageExt = "png"
    ) -> List[bytes]:
        """
        Convert a PDF document into a list of image byte representations.

        Parameters
        ----------
        pdf : PDFInput
            Either a filesystem path (str | Path) or raw PDF bytes.
        zoom : float, optional
            Rendering scale factor applied to each page (default is 0.2).
        ext : ImageExt, optional
            Output image format (e.g., "png", "jpeg").

        Returns
        -------
        List[bytes]
            A list of image bytes, one per PDF page.

        Raises
        ------
        ValueError
            If the PDF cannot be opened or validated.
        TypeError
            If the input type is unsupported.
        """
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
        """
        Convert a sequence of image byte streams into a single PDF document.

        Parameters
        ----------
        images : Iterable[bytes]
            Iterable containing image byte objects.
        allowed_formats : list[str], optional
            Allowed image formats for validation (default: ["png", "jpeg"]).

        Returns
        -------
        bytes
            The resulting PDF document as raw bytes.

        Raises
        ------
        ValueError
            If image validation fails or resulting PDF is invalid.
        """
        validate_image_bytes(images, allowed_formats)
        doc = pymupdf.open()
        for img_bytes in images:
            img_doc = pymupdf.open(stream=img_bytes, filetype=get_image_type(img_bytes))
            rect = img_doc[0].rect
            page = doc.new_page(width=rect.width, height=rect.height)
            page.insert_image(rect, stream=img_bytes)
            img_doc.close()
        pdf_bytes = doc.tobytes()
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
        """
        Convert a PDF to images and save each page to disk.

        Parameters
        ----------
        pdf : PDFInput
            Path to a PDF file or raw PDF bytes.
        output_path : str | Path
            Directory where images will be written. Must already exist.
        pdf_name : str | None, optional
            Base filename to use for output images. If not provided,
            derived from the PDF path when available.
        ext : ImageExt, optional
            Image file extension (default: "png").
        start : int, optional
            Starting index for page numbering (default: 0).

        Returns
        -------
        str
            The output directory path as a string.

        Raises
        ------
        ValueError
            If the output path is invalid or name resolution fails.
        """
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
        """
        Convert image bytes to a PDF and save the resulting file to disk.

        Parameters
        ----------
        images : Iterable[bytes]
            Iterable of image byte objects.
        output_path : str | Path
            Directory where the PDF will be saved. Must already exist.
        pdf_name : str
            Desired filename for the PDF (extension optional).

        Returns
        -------
        str
            Full path to the saved PDF file as a string.

        Raises
        ------
        ValueError
            If the output path is invalid or PDF validation fails.
        """
        pdf_name = self._validate_pdf_name(name=pdf_name)
        output_path = self._validate_path(output_path)
        pdf_path = output_path / pdf_name

        if pdf_path.suffix.lower() != ".pdf":
            pdf_path = pdf_path.with_suffix(".pdf")

        pdf_bytes = self.images_to_pdf(images)

        pdf_path.write_bytes(pdf_bytes)
        return pdf_path.as_posix()

    def _validate_pdf_name(
        self,
        pdf: PDFInput | None = None,
        name: str | None = None,
    ) -> str:
        """
        Determine a valid PDF base name.

        Parameters
        ----------
        pdf : PDFInput | None
            Original PDF source (path or bytes).
        name : str | None
            Explicitly provided filename.

        Returns
        -------
        str
            Valid base filename without extension.

        Raises
        ------
        ValueError
            If no valid name can be determined.
        """
        if name is not None:
            return name

        if isinstance(pdf, (str, Path)):
            return Path(pdf).stem

        raise ValueError(
            "Unable to determine PDF name. "
            "Provide either a file path (str or Path) or explicitly pass `name` "
            "when supplying raw PDF bytes."
        )

    def _validate_pdf_bytes(self, data):
        """
        Validate that provided bytes represent a valid PDF document.

        Parameters
        ----------
        data : bytes
            Byte content to validate.

        Raises
        ------
        ValueError
            If the data does not represent a valid PDF.
        """
        if not is_pdf_bytes(data):
            raise ValueError("Document is not pdf")

    def _validate_path(self, path: str | Path) -> Path:
        """
        Validate that a filesystem path exists and is resolvable.

        Parameters
        ----------
        path : str | Path
            Path to validate.

        Returns
        -------
        Path
            Resolved Path object.

        Raises
        ------
        ValueError
            If the path does not exist.
        """
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
