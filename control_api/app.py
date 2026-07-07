from fastapi import Depends, FastAPI

from control_api.dependencies import verify_api_key

import control_api.otherFile as otherFile
import control_api.results.results as results
import control_api.scripts.scripts as scripts
import control_api.settings.settings as settings

app = FastAPI()

app.include_router(otherFile.router)
app.include_router(results.router)
app.include_router(scripts.router)
app.include_router(settings.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Control API!"}

@app.get("/status")
async def status():
    return {"status": "ok"}

@app.get("/version")
async def version():
    return {"version": "1.0.0"}

@app.get("/echo/path/{message}")
async def echo_path(message: str):
    return {"message": message}

@app.get("/echo/query/")
async def echo(message: str = "No message provided"):
    return {"message": message}

@app.get("/secure-data/")
async def secure_data(_: None = Depends(verify_api_key)):
    return {"data": "This is some secure data!"}