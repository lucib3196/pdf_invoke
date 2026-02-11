from pdf_invoke.converter import PDFImageConverter
from pathlib import Path
import pytest
from pdf_invoke import MultiModalLLM, BaseOutput
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv


load_dotenv()


@pytest.fixture
def multimodal_llm():
    model = init_chat_model("gpt-4o", model_provider="openai")
    return MultiModalLLM(
        prompt="Summarize this for me",
        model=model,
    )


def test_model_initialization(multimodal_llm):
    assert multimodal_llm


@pytest.mark.parametrize("sample_pdf", ["path", "bytes"], indirect=True)
def test_invoke_pdf(multimodal_llm, sample_pdf):
    result = multimodal_llm.invoke(pdf=sample_pdf)
    assert result
    assert BaseOutput.model_validate(result).data


@pytest.mark.parametrize("sample_png", ["bytes", "path"], indirect=True)
def test_invoke_images(multimodal_llm, sample_png):
    result = multimodal_llm.invoke(images=[sample_png])
    assert result
    assert BaseOutput.model_validate(result).data





# Async test 
@pytest.mark.asyncio
@pytest.mark.parametrize("sample_pdf", ["path", "bytes"], indirect=True)
async def test_ainvoke_pdf(multimodal_llm, sample_pdf):
    result = await multimodal_llm.ainvoke(pdf=sample_pdf)
    assert result
    assert BaseOutput.model_validate(result).data

@pytest.mark.asyncio
@pytest.mark.parametrize("sample_png", ["bytes", "path"], indirect=True)
async def test_ainvoke_images(multimodal_llm, sample_png):
    result = await multimodal_llm.ainvoke(images=[sample_png])
    assert result
    assert BaseOutput.model_validate(result).data

