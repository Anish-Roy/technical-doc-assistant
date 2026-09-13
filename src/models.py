from pydantic import BaseModel


class Document(BaseModel):
    doc_id: str
    title: str
    url: str
    text: str
