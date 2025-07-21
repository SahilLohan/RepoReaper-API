
from pydantic import BaseModel
from typing import List

class AnalyzeRepoRequest(BaseModel):
    repo_url: str

class AnalyzeRepoResponse(BaseModel):
    data:str
    responseType:str
    status:bool
    message:str
    repo_name:str

class GenerateDocRequest(BaseModel):
    repo_name: str
    language: str

class GenerateDocResponse(BaseModel):
    data:str
    responseType:str
    status:bool
    message:str
