from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel

class PDFMultiModalLLM:
    def __init__(
        self,
        *,
        prompt: str,
        model: BaseChatModel,
        pdf: PDFInput | None = None,
        image_bytes: Sequence[bytes] | None = None,
    ):
        if pdf is None and image_bytes is None:
            raise ValueError("Either pdf_path or image_bytes must be provided")
        if pdf is not None and image_bytes is not None:
            raise ValueError("Provide only one of pdf_path or image_bytes")

        self.prompt = prompt
        self.builder = ImagePayloadBuilder()
        self.llm = model

        if pdf is not None:
            self.pdf_bytes = PDFImageConverter().convert_to_images(pdf)

        elif image_bytes:
            self.pdf_bytes = list(image_bytes)
        else:
            raise RuntimeError("Unexpected Error Occured ")

    def prepare_payload(self, mime="image/png"):
        try:
            image_payload = self.builder.prepare_llm_payload(self.pdf_bytes, mime=mime)
            message = {
                "role": "user",
                "content": [{"type": "text", "text": self.prompt}, *image_payload],
            }
            return message
        except Exception as e:
            raise RuntimeError(f"Failed to prepare payload for LLM. Error:  {e}")

    def invoke(
        self,
        output_model: Optional[Type[BaseModel]] = BaseOutput,
        mime: str = "image/png",
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
    ):
        message = self.prepare_payload()
        if output_model:
            chain = self.llm.with_structured_output(
                schema=output_model,
            )
            return chain.ainvoke([message])
        else:
            return self.llm.ainvoke([message])