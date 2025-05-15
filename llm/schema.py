from pydantic import BaseModel

class StructuredQuery(BaseModel):
    topic: str
    query: str
    n_results_lattest: int
    n_results_trending: int

class StructuredPaper(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    url: str