

# 📄 pdf-invoke

`pdf-invoke` is a lightweight utility for invoking multimodal LLMs using PDF files or image inputs.

It converts PDFs to images, prepares base64-encoded payloads, and sends them to a LangChain-compatible chat model with optional structured output support.

---

## Features

* Convert PDFs to images automatically
* Accept raw image bytes or file paths
* Prepare multimodal LLM payloads
* Support structured output via Pydantic models
* Sync and async invocation
* MIME type validation for image safety

---

## Installation

```bash
pip install pdf-invoke
```

---

## Quick Example

```python
from langchain_openai import ChatOpenAI
from pdf_invoke import MultiModalLLM

llm = ChatOpenAI(model="gpt-4o")

mm = MultiModalLLM(
    prompt="Extract the key information from this document.",
    model=llm,
)

response = mm.invoke(pdf="example.pdf")

print(response)
```

---

## Structured Output Example

```python
from pydantic import BaseModel

class ExtractedData(BaseModel):
    title: str
    summary: str

response = mm.invoke(
    pdf="example.pdf",
    output_model=ExtractedData,
)

print(response.title)
```

---

## Async Usage

```python
response = await mm.ainvoke(pdf="example.pdf")
```

---

## Accepted Inputs

You may provide:

* `pdf` → file path, `Path`, or raw PDF bytes
* `images` → list of image paths or image bytes

Only one of `pdf` or `images` may be provided per invocation.

---

## How It Works

1. PDF inputs are converted to images.
2. Images are validated and base64 encoded.
3. A multimodal payload is created.
4. The payload is sent to a LangChain chat model.
5. Optional structured output is enforced via Pydantic.

---

## Requirements

* Python 3.10+
* LangChain-compatible chat model
* Pydantic

---

## License

MIT License

---
