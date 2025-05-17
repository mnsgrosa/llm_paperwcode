from fastapi import FastAPI, HTTPException, WebSocket
from scraper.paperscraper import PaperScraper
from db.chroma import DBClient
from backend.schemas import PostPaperList, GetPaper, GetPaperResponse
from uuid import uuid4
import io

app = FastAPI()
scraper = PaperScraper()
db_trending = DBClient('/tmp/chroma/trending')
db_lattest = DBClient('/tmp/chroma/lattest')

message_queue = io.Queue()
agent_queue = io.Queue()

@app.post('/papers/post/')
def add_trending_papers(post_paper_list: PostPaperList):
    try:
        if post_paper_list.page == 'trending':
            db = db_trending
        elif post_paper_list.page == 'lattest':
            db = db_lattest
        else:
            raise HTTPException(status_code=400, detail='Invalid page')
        for paper in post_paper_list.papers:
            db.add_context(str(uuid4()), paper.content)
        return {'message': f'Papers added successfully to {post_paper_list.page}'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/')
def get_papers(get_paper : GetPaper):
    try:
        if get_paper.page == 'trending':
            db = db_trending
        elif get_paper.page == 'lattest':
            db = db_lattest
        else:
            raise HTTPException(status_code=400, detail='Invalid page')
        papers = db.query(get_paper.query, get_paper.n_results)
        return GetPaperResponse(papers = papers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket('/chat')
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    async def forward_agent_messages():
        while True:
            response = await agent_queue.get()
            await websocket.send_text(response)
            agent_queue.task_done()


    forward_task = io.create_task(forward_agent_messages())

    try:
        while True:
           message = await websocket.receive_text()
           if message == 'exit':
               break
           await message_queue.put(message)
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        forward_task.cancel()
        try:
            await forward_task
        except io.CancelledError:
            pass

@app.websocket('/agent_ws')
async def websocket_agent(websocket: WebSocket):
    await websocket.accept()

    async def forward_client_messages():
        while True:
            message = await message_queue.get()
            await websocket.send_text(message)
            message_queue.task_done()

    forward_task = io.create_task(forward_client_messages())

    try:
        while True:
            response = await websocket.receive_text()
            await agent_queue.put(response)
    except Exception as e:
        print(f"Agent WebSocket error: {e}")
    finally:
        forward_task.cancel()
        try:
            await forward_task
        except io.CancelledError:
            pass

    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8501)