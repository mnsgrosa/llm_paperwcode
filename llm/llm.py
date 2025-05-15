from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

class Researcher:
    def __init__(self, model = 'gemini-2.0-flash-exp'):
        self.model = model
        self.llm = GoogleGenerativeAI(api_key = os.getenv('GOOGLE_API_KEY'), model = self.model)
        self.context = {}

    def get_context(self, query:str):
        import httpx
        import json
        try:
            structured_query = self.llm.with_structured_output(StructuredQuery)
            topic_extractor = self.llm.invoke(
                ChatPromptTemplate.from_template([
                    ('system', 'You are a machine learning researcher'),
                    ('user', 'What is the topic of this query: {query}'),
                    ('output', 'topic: str')
                ])
            )
            structured_paper = self.llm.with_structured_output(StructuredPaper)
            query_orgnanized = structured_query.invoke(query)
            subject = topic_extractor.output
            n_results_lattest = query_orgnanized.n_results_lattest
            n_results_trending = query_orgnanized.n_results_trending
            with httpx.Client() as client:
                response_lattest = client.get(f'http://localhost:8501/papers/get/',
                            params = {
                                'page': 'lattest',
                                'query': subject,
                                'n_results': n_results_lattest
                                }
                            )
                response_trending = client.get(f'http://localhost:8501/papers/get/',
                            params = {
                                'page': 'trending',
                                'query': subject,
                                'n_results': n_results_trending 
                                }
                            )
                papers = []
                papers.extend(json.loads(response_lattest.text))
                papers.extend(json.loads(response_trending.text))
                self.raw_papers = papers    

            for paper in self.raw_papers:
                paper = structured_paper(paper)
                paper_schema = structured_paper.invoke(paper)
                self.context['title'].append(paper_schema.title)
                self.context['authors'].append(paper_schema.authors)
                self.context['abstract'].append(paper_schema.abstract)
                self.context['url'].append(paper.url)
            
            
            return papers
        except Exception as e:
            logging.error(f'Error getting context: {e}')
            return None
        

    def run(self, user_input):

        chat = ChatPromptTemplate.from_template([
            ('system', 'You are a machine learning researcher'),
            ('context', self.context),
            ('user', '{user_input}')
        ])
        return self.llm.invoke(chat.invoke(user_input))
            