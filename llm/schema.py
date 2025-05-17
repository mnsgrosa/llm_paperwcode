from pydantic import BaseModel

class StructuredQuery(BaseModel):
    query: str
    n_results_lattest: int
    n_results_trending: int

class PaperTopic(BaseModel):
    topic: str
    papers: list[StructuredPaper]

class StructuredPaper(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    url: str

class GetPaper(BaseModel):
    papers: list[StructuredPaper]