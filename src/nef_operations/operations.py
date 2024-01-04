# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 11:40:10
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-12-31 18:42:56
import requests
import json 

def login (ip, port, username, password):

    login_url = f"http://{ip}:{port}/api/v1/login/access-token"
    headers = {}
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }

    response = requests.post(
        url=login_url,
        headers=headers,
        data=data
    )
    
    # Check if the login was successful
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()


    print("Login Response:", response.text)
    resp_content = response.json()
    token = resp_content["access_token"]

    return token

def create_ue_movement_loop(ip, port, ue_supi, token):
    url = f"http://{ip}:{port}/api/v1/ue_movement/start-loop"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"
    data = {
        "supi": ue_supi
    }
    response = requests.post(
        url=url,
        headers=headers, 
        json=data
    )
    
    print("Initiated UE Movement", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()

def stop_ue_movement_loop(ip, port, ue_supi, token):
    url = f"http://{ip}:{port}/api/v1/ue_movement/stop-loop"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"

    data = {
        "supi": ue_supi
    }
    response = requests.post(
        url=url,
        headers=headers, 
        json=data
    )
    
    
    print("Terminated UE Movement", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()



def get_ues(ip, port, token):

    url = f"http://{ip}:{port}/api/v1/UEs"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"
    

    response = requests.get(
        url=url,
        headers=headers, 
    )
    
    print("Get UEs Response:", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()


def subscribe_event (ip, port, callback_url, monitoring_type,
                     monitoring_expire_time, token):

    url = f"http://{ip}:{port}/nef/api/v1/3gpp-monitoring-event/" \
        "v1/netapp/subscriptions"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"
    
    monitoring_payload = {
        "externalId": "123456789@domain.com",
        "notificationDestination": callback_url,
        "monitoringType": monitoring_type,
        "maximumNumberOfReports": 1,
        "monitorExpireTime": monitoring_expire_time,
        "maximumDetectionTime": 1,
        "reachabilityType": "DATA"
    }

    response = requests.post(
        url=url,
        headers=headers, 
        data=json.dumps(monitoring_payload)
    )
    
    print("Monitoring Subscription Response:", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()

    


def create_ue(ip, port, ue_name, ue_description, 
              ue_ipv4, ue_ipv6, ue_mac, ue_supi, token):
    
    url = f"http://{ip}:{port}/api/v1/UEs"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"
    
    payload = {
        "name": ue_name,
        "description": ue_description,
        "ip_address_v4": ue_ipv4,
        "ip_address_v6": ue_ipv6,
        "mac_address": ue_mac,
        "supi": ue_supi,
    }
    
    response = requests.post(
        url=url,
        headers=headers, 
        data=json.dumps(payload)
    )
    
    print("Create UE Response:", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()



def get_ue_path_loss(ip, port, ue_supi, token):
    print("starting....")
    url = f"http://{ip}:{port}/api/v1/UEs/{ue_supi}/path_losses"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"

    response = requests.get(
        url=url,
        headers=headers, 
    )
    
    print("Get UEs Path Losses Information:", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()

def get_serving_cell_info(ip, port, ue_supi, token):
    # To get the Serving Cell Info, we required to start a new UE Movement Loop
    create_ue_movement_loop(
        ip, port, ue_supi, token
    )

    url = f"http://{ip}:{port}/api/v1/UEs/{ue_supi}/serving_cell"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"

    response = requests.get(
        url=url,
        headers=headers, 
    )
    
    print("Get UE Serving Cell Information", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()
    
    stop_ue_movement_loop(
        ip, port, ue_supi, token
    )

def get_ue_handover_event(ip, port, ue_supi, token):
    print("starting....")
    url = f"http://{ip}:{port}/test/api/v1/UEs/{ue_supi}/handovers"
    print(f"URL: {url}")
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"

    response = requests.get(
        url=url,
        headers=headers, 
    )
    
    print("Get UEs Handovers Information:", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()

def subscribe_qos_event (ip, port, callback_url, token):

    url = f"http://{ip}:{port}/nef/api/v1/3gpp-as-session-with-qos/" \
        "v1/netapp/subscriptions"
        
    headers = {}
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"
    
    monitoring_payload = {
        "ipv4Addr": "10.0.0.0",
        "ipv6Addr": "0:0:0:0:0:0:0:0",
        "macAddr": "22-00-00-00-00-00",
        "notificationDestination": callback_url,
        "snssai": {
            "sst": 1,
            "sd": "000001"
        },
        "dnn": "province1.mnc01.mcc202.gprs",
        "qosReference": 9,
        "altQoSReferences": [
            0
        ],
        "usageThreshold": {
            "duration": 0,
            "totalVolume": 0,
            "downlinkVolume": 0,
            "uplinkVolume": 0
        },
        "qosMonInfo": {
            "reqQosMonParams": [
            "DOWNLINK"
            ],
            "repFreqs": [
            "EVENT_TRIGGERED"
            ],
            "latThreshDl": 0,
            "latThreshUl": 0,
            "latThreshRp": 0,
            "waitTime": 0,
            "repPeriod": 0
        }
    }

    response = requests.post(
        url=url,
        headers=headers, 
        data=json.dumps(monitoring_payload)
    )
    
    print("QoS Subscription Response:", response.text)
    if response.status_code not in [200, 201, 409]:
        response.raise_for_status()