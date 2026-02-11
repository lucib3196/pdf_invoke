from base64 import b64encode
from typing import Iterable, Literal, Optional, Sequence, Type

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

from pdf_invoke.converter import PDFImageConverter
from pdf_invoke.types import PDFInput
from pdf_invoke.utils import validate_image_bytes


ALLOWED_MIME = Literal["image/jpeg", "image/png"]

class BaseOutput(BaseModel):
    data: str


class MultiModalLLM:
    def __init__(
        self,
        *,
        prompt: str,
        model: BaseChatModel,
        pdf: PDFInput | None = None,
        image_bytes: Sequence[bytes] | None = None,
    ):
        # Base configuration
        self.prompt = prompt
        self.llm = model

        if pdf is None and image_bytes is None:
            raise ValueError("Either pdfinput or image_bytes must be provided")
        if pdf is not None and image_bytes is not None:
            raise ValueError("Provide only one of pdfinput or image_bytes")

        if pdf is not None:
            self.pdf_bytes = PDFImageConverter().pdf_to_images(pdf)

        elif image_bytes:
            self.pdf_bytes = list(image_bytes)
        else:
            raise RuntimeError("Unexpected Error Occured ")

    def invoke(
        self,
        output_model: Optional[Type[BaseModel]] = BaseOutput,
        mime: ALLOWED_MIME = "image/png",
    ):
        try:
            message = self.prepare_payload(mime)
            if output_model:
                chain = self.llm.with_structured_output(schema=output_model)
                return chain.invoke([message])
            else:
                return self.llm.invoke([message])
        except Exception as e:
            raise RuntimeError(f"Failed to invoke model {e}")

    async def ainvoke(
        self,
        output_model: Optional[Type[BaseModel]] = BaseOutput,
        mime: ALLOWED_MIME = "image/png",
    ):
        message = self.prepare_payload(mime)
        if output_model:
            chain = self.llm.with_structured_output(
                schema=output_model,
            )
            return chain.ainvoke([message])
        else:
            return self.llm.ainvoke([message])

    def prepare_payload(self, mime: ALLOWED_MIME = "image/png"):
        try:
            image_payload = self.prepare_image_payload(self.pdf_bytes, mime=mime)
            message = {
                "role": "user",
                "content": [{"type": "text", "text": self.prompt}, *image_payload],
            }
            return message
        except Exception as e:
            raise RuntimeError(f"Failed to prepare payload for LLM. Error:  {e}")

    def prepare_image_payload(
        self,
        payload: Iterable[bytes],
        mime: ALLOWED_MIME = "image/png",
    ):
        allowed_format = mime.split("/")[-1]
        validate_image_bytes(payload, allowed_formats=set(allowed_format))
        return [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{b64encode(p).decode("utf-8")}"
                },
            }
            for p in payload
        ]
