from pydantic import BaseModel, Field

class PostPaper(BaseModel):
    content: str = Field(exclude_none = True)

class PostPaperList(BaseModel):
    page: str = Field(exclude_none = True)
    papers: List[PostPaper]

class GetPaper(BaseModel):
    query: str = Field(exclude_none = True)
    n_results: int = Field(exclude_none = True)

class GetPaperResponse(BaseModel):
    page: str = Field(exclude_none = True)
    papers: List[str]