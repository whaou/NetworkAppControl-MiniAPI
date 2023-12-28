# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 10:53:45
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-12-26 17:25:09
from fastapi import FastAPI, Path, Response, status, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from db import crud, models
from db.database import SessionLocal, engine
import schemas.types as schemas
from requests.structures import CaseInsensitiveDict
import requests
import json
import os
from aux import variables
from aux.operations_ids import OPERATION
from nef_operations import operations as nef_operations
from performance_operations import operations as perf_operations
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


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
async def start_test(
    operation_id: int,
    is_server: bool = False,
    server_ip: str = None,
    is_cnf: bool = False):
    try:
        if operation_id == OPERATION.LOGIN.value:
            token = nef_operations.login(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                username=variables.VARIABLES["NEF_LOGIN_USERNAME"],
                password=variables.VARIABLES["NEF_LOGIN_PASSWORD"],
            )
            variables.VARIABLES["AUTH_TOKEN"] = token
            return JSONResponse(content="Login Done", status_code=200)
        
        if operation_id == OPERATION.CREATE_UE.value:
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
        
        if operation_id == OPERATION.GET_UES.value:
            nef_operations.get_ues(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Got UEs", status_code=200)
        
        if operation_id == OPERATION.SUBSCRIPTION.value:
            nef_operations.subscribe_event(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                callback_url=variables.VARIABLES["SUBS1_CALLBACK_URL"],
                monitoring_type=variables.VARIABLES["SUBS1_MONITORING_TYPE"],
                monitoring_expire_time=variables.VARIABLES["SUBS1_MONITORING_EXPIRE_TIME"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Subscription Done", status_code=200)
        if operation_id == OPERATION.UE_PATH_LOSS.value:
            nef_operations.get_ue_path_loss(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                  ue_supi=variables.VARIABLES["UE1_SUPI"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Got UE Path Loss Information", status_code=200)
        if operation_id == OPERATION.SERVING_CELL_INFO.value:
            nef_operations.get_serving_cell_info(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                ue_supi=variables.VARIABLES["UE1_SUPI"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Got UE Serving Cell Information", status_code=200)
        
        if operation_id == OPERATION.HANDOVER.value:
            nef_operations.get_ue_handover_event(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                ue_supi=variables.VARIABLES["UE1_SUPI"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="Subscription Done", status_code=200)

        if operation_id == OPERATION.E2E_UE_PERFORMANCE.value:
            perf_operations.run_iperf_test(is_server, server_ip)
            _type = "Server" if is_server else "Client"
            return JSONResponse(content=f"Started E2E UE Performance Test, as  {_type} Side", status_code=200)
        
        if operation_id == OPERATION.E2E_UE_RTT_PERFORMANCE.value:
            if not is_cnf:
                perf_operations.start_ping(server_ip)
            else:
                perf_operations.start_hping(server_ip)
            return JSONResponse(content=f"Started E2E UE RTT Performance Test", status_code=200)


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

@app.get("/results/{operation_id}")
async def get_report(operation_id: int):
    
    if operation_id == OPERATION.E2E_UE_PERFORMANCE.value:
        return FileResponse(path=f'./static/{variables.E2E_RESULTS}')

    if operation_id == OPERATION.E2E_UE_RTT_PERFORMANCE.value:
        return FileResponse(path=f'./static/{variables.E2E_RTT_RESULTS}')


@app.post("/stop/{operation_id}")
async def stop_test(operation_id: int):
    try:
        if operation_id ==OPERATION.E2E_UE_PERFORMANCE.value:
            os.remove(f'./static/{variables.E2E_RESULTS}')
            return JSONResponse(content="Sucessfully Cleaned Up test environment", status_code=200)
        
        if operation_id ==OPERATION.E2E_UE_PERFORMANCE.value:
            os.remove(f'./static/{variables.E2E_RTT_RESULTS}')
            return JSONResponse(content="Sucessfully Cleaned Up test environment", status_code=200)
     
    except Exception as e:
        return JSONResponse(content=f"Error: {e}", status_code=400)

