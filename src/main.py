from typing import Any
from fastapi import Request, FastAPI, Response, status
from fastapi.responses import JSONResponse, FileResponse

from fastapi.encoders import jsonable_encoder

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .db import crud, models
from .db.database import SessionLocal, engine
from src import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"Server says It's All Good"}

@app.get("/info")
async def get_info():
    # Define get_info() function logic here
    pass

@app.post("/configStream", status_code=status.HTTP_201_CREATED)
async def config_stream(config: schemas.StreamConfig, 
                        response: Response,
                        db: Session = Depends(get_db),):
    
    json_data = jsonable_encoder(config.dict(exclude_unset=True))

    stream = crud.create_stream_config(db, json_data)

    response.headers["Location"] = f"/configStream/{stream.id}"
    return stream.id

@app.post("/start")
async def start_test(configId: int, duration: int):
    # Define start_test() function logic here
    pass

@app.get("/status")
async def get_status(runId: int):
    # Define get_status() function logic here
    pass

@app.post("/abort")
async def abort_test(runId: int):
    # Define abort_test() function logic here
    pass

@app.get("/report")
async def get_report(runId: int):
    # Define get_report() function logic here
    pass