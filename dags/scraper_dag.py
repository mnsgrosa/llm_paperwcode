from airflow.sdk import asset

@asset(schedule = '@daily')
def scrape_papers_to_db():
    from scraper.paperscraper import PaperScraper
    scraper = PaperScraper()
    latest_papers = scraper.returnable_text(page = 'lattest')
    trending_papers = scraper.returnable_text(page = 'trending')
    return latest_papers, trending_papers

@asset(schedule = [scrape_papers_to_db])
def add_papers_to_db(context: dict):
    from backend.schemas import PostPaperList
    import httpx
    latest_papers = context['ti'].xcom_pull(
        dag_id = 'scrape_papers_to_db',
        task_id = 'scrape_papers_to_db',
        key = 'return_value',
        include_prior_dates = True
    )[0]
    trending_papers = context['ti'].xcom_pull(
        dag_id = 'scrape_papers_to_db',
        task_id = 'scrape_papers_to_db',
        key = 'return_value',
        include_prior_dates = True
    )[1]
    try:
        with httpx.Client() as client:
            latest_papers = PostPaperList(page = 'lattest', papers = latest_papers)
            trending_papers = PostPaperList(page = 'trending', papers = trending_papers)
            client.post('http://localhost:8501/papers/post/', params = latest_papers.dict())
            client.post('http://localhost:8501/papers/post/', params = trending_papers.dict())
        return True
    except Exception as e:
        logging.error(f'Error adding papers to db: {e}')
        return False
        