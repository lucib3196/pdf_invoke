from pathlib import Path
import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_pdf(request):
    method = request.param
    path = FIXTURES_DIR / "sample.pdf"
    if method == "path":
        return path
    elif method == "bytes":
        return path.read_bytes()
    else:
        raise ValueError(
            f"Incorrect request passed in for fixture sample_pdf expected bytes or path received {method}"
        )


@pytest.fixture
def sample_png(request):
    method = request.param
    path = FIXTURES_DIR / "sample.png"
    if method == "path":
        return path
    elif method == "bytes":
        return path.read_bytes()
    else:
        raise ValueError(
            f"Incorrect request passed in for fixture sample_pdf expected bytes or path received {method}"
        )
