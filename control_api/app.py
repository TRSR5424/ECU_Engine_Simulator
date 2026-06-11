from fastapi import FastAPI, Depends

from dependencies import verify_api_key

import otherFile
import results.results as results

app = FastAPI()

app.include_router(otherFile.router)
app.include_router(results.router)

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