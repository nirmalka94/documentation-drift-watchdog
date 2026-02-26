from fastapi import FastAPI, Request
import uvicorn
import asyncio
from core.trigger import handle_trigger_event

app = FastAPI()

@app.post("/trigger")
async def trigger(request: Request):
    payload = await request.json()
    config = request.app.state.config
    await handle_trigger_event(payload, config)
    return {"status": "triggered"}

def run_webapi(config):
    app.state.config = config
    uvicorn.run(app, host=config.get("WEBAPI_HOST", "0.0.0.0"), port=int(config.get("WEBAPI_PORT", 8000)))
