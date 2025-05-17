import asyncio
import websockets
import json
from fastapi import FastAPI
import uvicorn
from llm.researcher import Researcher

app = FastAPI()
researcher = Researcher()

async def handle_llm_websocket(websocket, path):
    print("LLM WebSocket connected")
    try:
        async for message in websocket:
            try:
                response = await researcher.run(message)
                await websocket.send(json.dumps({"response": response}))
            except Exception as e:
                error_msg = f"Error processing message: {str(e)}"
                print(error_msg)
                await websocket.send(json.dumps({"error": error_msg}))
    except websockets.exceptions.ConnectionClosed:
        print("LLM WebSocket disconnected")

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handle_llm_websocket, "0.0.0.0", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == "__main__":
    import threading
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)