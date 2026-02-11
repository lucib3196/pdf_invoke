from pdf_invoke.converter import PDFImageConverter
from pathlib import Path
import pytest


@pytest.mark.parametrize("sample_pdf", ["path", "bytes"], indirect=True)
def test_convert_pdf_to_images(sample_pdf):
    converter = PDFImageConverter()
    images = converter.pdf_to_images(sample_pdf)
    assert isinstance(images, list)
    assert len(images) > 0
    assert all(isinstance(img, bytes) for img in images)


@pytest.mark.parametrize("sample_pdf", ["path", "bytes"], indirect=True)
def test_save_pdf_to_images(tmp_path, sample_pdf):
    converter = PDFImageConverter()
    output_path = converter.save_pdf_to_images(
        sample_pdf, output_path=tmp_path, pdf_name="pdf_test"
    )
    output_path = Path(output_path)
    assert list(output_path.iterdir())
    # The naming is split so we sort based on some the int value
    for idx, p in enumerate(
        sorted(output_path.iterdir(), key=lambda p: int(p.stem.split("_")[-1]))
    ):
        assert p.stem == f"pdf_test_page_{idx}"


@pytest.mark.parametrize("sample_png", ["bytes"], indirect=True)
def test_images_to_pdf(sample_png):
    converter = PDFImageConverter()
    pdf = converter.images_to_pdf([sample_png])
    assert isinstance(pdf, bytes)


@pytest.mark.parametrize("sample_png", ["bytes"], indirect=True)
def test_save_images_to_pdf(tmp_path, sample_png):
    converter = PDFImageConverter()
    pdf_path = converter.save_images_to_pdf([sample_png], tmp_path, pdf_name="pdf_test")
    pdf_path = Path(pdf_path)
    assert pdf_path.exists()
    assert pdf_path.suffix.lower() == ".pdf"
    assert pdf_path.stem == "pdf_test"
