import httpx
import json
import logging
from bs4 import BeautifulSoup

class PaperScraper:
    def __init__(self):
        self.base_url = 'https://paperswithcode.com'
        self.latest = '/latest'

    async def get_papers_soup(self, page: str = 'lattest'):
        async with httpx.AsyncClient() as client:
            if page == 'lattest':
                response = await client.get(self.base_url + self.latest)
            elif page == 'trending':
                response = await client.get(self.base_url)
            else:
                logging.error(f'Invalid page: {page}')
                return
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.paper_tittles = soup.find_all('a', href=lambda href: href and '/paper/' in href)
                return self.paper_tittles
            except Exception as e:
                logging.error(f'Error getting the papers: {e}')
                return

    async def get_papers_link(self):
        self.papers_link = [self.base_url + title['href'] for title in self.paper_tittles]
        return self.papers_link

    async def get_papers_abstract(self):
        self.papers_abstract = []
        for link in self.papers_link:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    abstract_div = soup.find('div', class_='paper-abstract')
                    p_tag = abstract_div.find('p')
                    abstract_text = p_tag.text.strip()
                    self.papers_abstract.append(abstract_text)
                except Exception as e:
                    logging.error(f'Error getting the abstract for {link}: {e}')
                    self.papers_abstract.append(None)
        return self.papers_abstract

    async def get_papers_github(self):
        self.papers_github = []
        for link in self.papers_link:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    github_links = soup.find('a', href=lambda href: href and 'github.com' in href)
                    self.papers_github.append(github_links)
                except Exception as e:
                    logging.error(f'Error getting the github link for {link}: {e}')
                    self.papers_github.append(None)
        return self.papers_github

    async def returnable_text(self, page: str = 'lattest'):
        await self.get_papers_soup(page)
        await self.get_papers_link()
        await self.get_papers_abstract()
        await self.get_papers_github()
        self.papers = []
        print(f"Lengths: titles={len(self.paper_tittles)}, abstracts={len(self.papers_abstract)}, github={len(self.papers_github)}")
        for i in range(len(self.paper_tittles)):
            github_text = self.papers_github[i].text if self.papers_github[i] is not None else "No GitHub link"
            self.papers.append(
                '{title} {abstract} {github}'.format(
                    title = self.paper_tittles[i].text,
                    abstract = self.papers_abstract[i] if self.papers_abstract[i] is not None else "No abstract",
                    github = github_text
                )
            )
        return self.papers