import logging
from typing import Dict, List
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import httpx
from pydantic import BaseModel

load_dotenv()

class StructuredPaper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    url: str

class StructuredQuery(BaseModel):
    n_results_lattest: int = 3
    n_results_trending: int = 3

class Researcher:
    def __init__(self, model: str = 'gemini-2.0-flash-exp'):
        self.model = model
        self.llm = GoogleGenerativeAI(api_key=os.getenv('GOOGLE_API_KEY'), model=self.model)
        self.context = {}
        self.history = []

    async def get_context(self, query: str):
        try:
            topic = await self.extract_topic(query)
            if topic in self.context:
                return self.context[topic]
            else:
                structured_query = await self.structure_query(query)
                
                async with httpx.AsyncClient() as client:
                    papers = await self.fetch_papers(client, topic, structured_query)
                
                structured_papers = await self.process_papers(papers)
                
                return self.context[topic]
            
        except Exception as e:
            logging.error(f'Error getting context: {e}')
            return None

    async def extract_topic(self, query: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a machine learning researcher. Extract the main topic from the user's query."),
            ("user", "Query: {query}"),
            ("output", "topic: str")
        ])
        response = await self.llm.ainvoke(prompt.invoke({"query": query}))
        return response.content.strip()

    async def structure_query(self, query: str) -> StructuredQuery:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze the query and determine how many papers to fetch from latest and trending."),
            ("user", "Query: {query}"),
            ("output", "n_results_lattest: int\nn_results_trending: int")
        ])
        response = await self.llm.with_structured_output(StructuredQuery).ainvoke(prompt.invoke({"query": query}))
        return response

    async def fetch_papers(self, client: httpx.AsyncClient, topic: str, query: StructuredQuery):
        base_url = "http://localhost:8501/papers/get/"
        params = {
            'page': 'lattest',
            'query': topic,
            'n_results': query.n_results_lattest
        }
        
        responses = []
        for page in ['lattest', 'trending']:
            params['page'] = page
            params['n_results'] = query.n_results_lattest if page == 'lattest' else query.n_results_trending
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            responses.extend(response.json()['papers'])
        
        return responses

    async def process_papers(self, papers: GetPaper):
        structured_papers = []
        for paper in papers.papers:
            try:
                output_structure = self.llm.with_structured_output(StructuredPaper)
                structured_output = output_structure.ainvoke(ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful AI research assistant."),
                    ("human", "Paper: {paper}"),
                ]).invoke({"paper": paper}))
                structured_papers.append(structured_output)
            except Exception as e:
                logging.error(f"Error processing paper: {e}")
        return structured_papers

    async def run(self, user_input: str):
        structured_query = await self.get_context(user_input)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI research assistant."),
            ("system", f"Context from papers:\nTitles: {self.context['titles']}\nAbstracts: {self.context['abstracts']}"),
            ("human", "{input}")
        ])
        
        response = await self.llm.ainvoke(prompt.invoke({"input": user_input}))
        return response.content