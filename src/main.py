# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 10:53:45
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-12-31 18:42:45
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
import signal
from aux import variables
from aux.operations_ids import OPERATION
from nef_operations import operations as nef_operations
from performance_operations import operations as perf_operations
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

RUNNING_PROCESSES = {
    OPERATION.MAX_CONNECTIONS.value: [],
    OPERATION.MAX_HOPS.value: [],
    OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value: []
}

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
    operation_id: str,
    is_server: bool = False,
    target_ip: str = None,
    target_port: int = None,
    target: str = None):
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

        if operation_id == OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value:
            # Delete old results file
            if os.path.exists(
                f'./static/{variables.E2E_SINGLE_UE_THROUGHPUT_AND_LATENCY}'
            ):
                os.remove(
                    f'./static/{variables.E2E_SINGLE_UE_THROUGHPUT_AND_LATENCY}'
                )
            
            error_message = None
            # If the current MiniAPI is a client
            if not is_server:
                # Now, we can run iperf3 in a indpendent process
                iperf_server_process = perf_operations.start_iperf_client(
                    target_ip=target_ip,
                    number_of_streams=1
                )
                
                if not iperf_server_process:
                    error_message = "Couldn't start Iperf3 Client. Thus, the"\
                    "E2E Single UE Throughput and Latency Test could not be "\
                    "started!"
            else:
                iperf_server_process = perf_operations.start_iperf_server()
                
                if not iperf_server_process:
                    error_message = "Couldn't start Iperf3 Server. Thus, the"\
                    "E2E Single UE Throughput and Latency Test could not be "\
                    "started!" 
                else:
                    # Save to process to kill it later, when /stop is invoked
                    RUNNING_PROCESSES[
                        OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value
                    ].append(iperf_server_process)
            
            if error_message:
                return JSONResponse(
                    content=error_message,
                    status_code=400
            )
                
            return JSONResponse(
                content=f"Started E2E Single UE Throughput and Latency "
                "Performance Test",
                status_code=200
            )
            
            


        if operation_id == OPERATION.MAX_HOPS.value:
            # Delete old results file
            if os.path.exists(f'./static/{variables.MAX_HOPS_RESULTS}'):
                os.remove(f'./static/{variables.MAX_HOPS_RESULTS}')
                
            # Start the number of hops until target process
            max_hops_process = perf_operations.start_max_hops_computing(
                target
            )
            # Save to process to kill it later, when /stop is invoked
            RUNNING_PROCESSES[OPERATION.MAX_HOPS.value].append(
                max_hops_process
            )
            
            return JSONResponse(
                content=f"Started Max Hops Performance Test",
                status_code=200
            )

        if operation_id == OPERATION.MAX_CONNECTIONS.value:
            # Delete old results file
            if os.path.exists(f'./static/{variables.E2E_RESULTS}'):
                os.remove(f'./static/{variables.E2E_RESULTS}')
            # Start the netstat loop
            netstat_process = perf_operations.start_netstat_command()
            
            # If we can start a monitoring process everything is ok
            if netstat_process:
                # Save to process to kill it later, when /stop is invoked
                RUNNING_PROCESSES[OPERATION.MAX_CONNECTIONS.value].append(
                    netstat_process
                )
                print("Connections monitoring process was started...")
                return JSONResponse(
                    content="Connections monitoring process was started...",
                    status_code=200
                )
            # If we couldn't start a monitoring process, inform the client
            else:
                print("Could not start the connections monitoring process")
                return JSONResponse(
                    content="Could not start the connections monitoring " +
                    "process",
                    status_code=400
                )
            
        if operation_id == OPERATION.SUBSCRIBE_QOS_EVENT.value:
            nef_operations.subscribe_qos_event(
                ip=variables.VARIABLES["NEF_IP"],
                port=variables.VARIABLES["NEF_PORT"],
                callback_url=variables.VARIABLES["SUBS1_CALLBACK_URL"],
                token = variables.VARIABLES["AUTH_TOKEN"]
            )
            return JSONResponse(content="QoS Subscription Done", status_code=200)

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
async def get_report(operation_id: str):
    
    if operation_id == OPERATION.MAX_CONNECTIONS.value:
        return FileResponse(
            path=f'./static/{variables.MAX_CONNECTIONS_RESULTS}'
        )

    if operation_id == OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value:
        # The test may still be running when the user requests its results
        try:
            with open(
                f'./static/{variables.E2E_SINGLE_UE_THROUGHPUT_AND_LATENCY}',
                "r"
            ) as file:
                data = json.load(file)

                throughput_mbps, mean_rtt_ms = perf_operations\
                    .process_iperf_results(data)

                return JSONResponse(
                    content={
                        "throughput_mbps": throughput_mbps,
                        "mean_rtt_ms": mean_rtt_ms
                    },
                    status_code=200
                )
        except:
            return JSONResponse(
                content="The E2E Single UE Throughput and Latency Performance "
                "Test is not finished yet!",
                status_code=404
            )
        
    
    if operation_id == OPERATION.MAX_HOPS.value:
        # The test may still be running when the user requests its results
        if not os.path.exists(f'./static/{variables.MAX_HOPS_RESULTS}'):
            return JSONResponse(
                content=f"The Max Hops Performance Test is not finished yet!",
                status_code=404
            )
        
        with open(f'./static/{variables.MAX_HOPS_RESULTS}', "r") as file:
            data = json.load(file)
            return JSONResponse(
                content=data,
                status_code=200
            )
        

@app.post("/stop/{operation_id}")
async def stop_test(operation_id: str):
    try:
        if operation_id == OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value:
            while RUNNING_PROCESSES[
                OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value
            ]:
                rp = RUNNING_PROCESSES[
                    OPERATION.E2E_SINGLE_UE_LATENCY_AND_THROUGHPUT.value
                ].pop()
                print(f"Will kill Iperf3 Server Process with PID {rp.pid}")
                # Force the termination of the process
                os.killpg(os.getpgid(rp.pid), signal.SIGTERM)
                # Wait for the process to complete after termination/kill
                rp.wait()
                print(
                    f"Iperf3 Server Process with PID {rp.pid} was terminated"
                )
            return JSONResponse(
                content="Sucessfully Stopped the E2E Single UE Throughput and "
                "Latency Performance Test",
                status_code=200
            )
        
        
        if operation_id == OPERATION.MAX_HOPS.value:
            while RUNNING_PROCESSES[OPERATION.MAX_HOPS.value]:
                rp = RUNNING_PROCESSES[OPERATION.MAX_HOPS.value].pop()
                print(f"Will kill Hops Computing Process with PID {rp.pid}")
                # Force the termination of the process
                rp.terminate()
                # If terminate() doesn't work, use kill()
                if rp.is_alive():
                    rp.kill()
                # Wait for the process to complete after termination/kill
                rp.join()
                print(
                    f"Hops Computing Process with PID {rp.pid} was terminated"
                )
            return JSONResponse(
                content="Sucessfully Stopped the Max Hops Performance Test",
                status_code=200
            )
        
 
        if operation_id == OPERATION.MAX_CONNECTIONS.value:
            
            while RUNNING_PROCESSES[OPERATION.MAX_CONNECTIONS.value]:
                rp = RUNNING_PROCESSES[OPERATION.MAX_CONNECTIONS.value].pop()
                print(f"Will kill Netstat Process with PID {rp.pid}")
                # Force kill the process (send SIGKILL)
                os.killpg(os.getpgid(rp.pid), signal.SIGTERM)
                # Wait for the process to complete after termination/kill
                rp.wait()
                print(f"Netstat Process with PID {rp.pid} was terminated")

            return JSONResponse(content="Sucessfully Cleaned Up test environment", status_code=200)

    except Exception as e:
        return JSONResponse(content=f"Error: {e}", status_code=400)

