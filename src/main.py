# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 10:53:45
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-05-22 13:16:45
from fastapi import FastAPI, Response, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from db import crud, models
from db.database import SessionLocal, engine
import schemas.types as schemas
from requests.structures import CaseInsensitiveDict
import requests
import json
from aux import variables
from nef_operations.operations_ids import NEF_OPERATION
from nef_operations import operations as nef_operations

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


@app.post("/configure", status_code=status.HTTP_200_OK)
async def configure(payload: schemas.Configuration):
    # Set variables
    print(payload.variables)
    variables.VARIABLES = payload.variables
    
    return JSONResponse(content="Variables Saved!", status_code=200)




@app.post("/start/{operation_id}")
async def start_test(operation_id: int):
    try:
        if operation_id == NEF_OPERATION.LOGIN.value:
            token = nef_operations.login(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                username=variables.VARIABLES["NEF_LOGIN_USERNAME"],
                password=variables.VARIABLES["NEF_LOGIN_PASSWORD"],
            )
            variables.VARIABLES["AUTH_TOKEN"] = token
            return JSONResponse(content="Login Done", status_code=200)
        
        if operation_id == NEF_OPERATION.CREATE_UE.value:
            nef_operations.create_ue(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                ue_name=variables.VARIABLES["UE1_NAME"],
                ue_description=variables.VARIABLES["UE1_DESCRIPTION"],
                ue_ipv4=variables.VARIABLES["UE1_IPV4"],
                ue_ipv6=variables.VARIABLES["UE1_IPV6"],
                ue_mac=variables.VARIABLES["UE1_MAC_ADDRESS"],
                ue_supi=variables.VARIABLES["UE1_SUPI"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Created UE", status_code=200)
        
        if operation_id == NEF_OPERATION.GET_UES.value:
            nef_operations.get_ues(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Got UEs", status_code=200)
        
        if operation_id == NEF_OPERATION.SUBSCRIPTION.value:
            nef_operations.subscribe_event(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                callback_url=variables.VARIABLES["SUBS1_CALLBACK_URL"],
                monitoring_type=variables.VARIABLES["SUBS1_MONITORING_TYPE"],
                monitoring_expire_time=variables.VARIABLES["SUBS1_MONITORING_EXPIRE_TIME"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Subscription Done", status_code=200)
    
    except Exception as e:
        return JSONResponse(content=f"Error: {e}", status_code=400)

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