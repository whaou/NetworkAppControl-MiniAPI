
import subprocess
import aux.variables as variables
from aux.ping_wrapper import PingWrapperThread
import pingparsing
from aux.ping_wrapper import parse_hping_output
import json
import os

def start_iperf_server():
    # Command to start the iperf3 server
    command = "iperf3 -s -1 &"

    # Run the command as a background process
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Optional: Print the process ID (PID) if needed
    print("iperf3 server process ID:", process.pid)

def start_iperf_client(server_ip):
    process = subprocess.Popen(
        f'iperf3 -t 5 -c {server_ip} -J > ./static/{variables.E2E_RESULTS}',
        stdout=subprocess.PIPE,
        shell=True)

def run_iperf_test(is_server: bool = False, server_ip = None):
    if is_server:
        print("Starting Server....")
        start_iperf_server()
    else:
        print("Starting Client....")
        start_iperf_client(server_ip)
    return "OK"


def start_ping(target_ip):
    ping_parser = pingparsing.PingParsing()
    transmiter = pingparsing.PingTransmitter()
    wrapper = PingWrapperThread(
        target=target_ip,
        parser=ping_parser,
        transmitter=transmiter
    )
    wrapper.start()
    wrapper.join()

def start_hping(target_ip):
    host, port = target_ip.split(":")
    if host == None or port == None:
        raise("Error!")
    try:
        # Run hping3 command
        command = f"hping3 -S -c 5 {host} -p {port}"
        output = subprocess.check_output(command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True)

        # Parse the output
        parsed_output = parse_hping_output(output)
        with open(f'./static/{variables.E2E_RTT_RESULTS}', 'w') as json_file:
            json.dump(parsed_output, json_file)
        return parsed_output
    except subprocess.CalledProcessError as e:
        print(f"Error running hping3: {e}")
        return None

def create_process_group():
    os.setpgrp()
    
def start_netstat_command():
    
    if os.system(f"netstat --version > /dev/null") == 0:
        base_command = "netstat -an | grep \"ESTABLISHED\""
    elif os.system(f"ss --version > /dev/null") == 0:
        base_command = "ss -t state established"
    else:
        return None
            
    # Command to start the netsat connections monitoring loop
    # The monitoring will run for 300 seconds and then stop.
    # This process can also be killed by invoking the /stop endpoint
    command = "start_time=$(date +%s); while true; do current_time=$(date " \
        "+%s); elapsed_time=$((current_time - start_time)); if " \
        f"[ $elapsed_time -ge 300 ]; then break; fi; {base_command} " \
        "| wc -l >> " \
        f"./static/{variables.MAX_CONNECTIONS_RESULTS}; sleep 1; done"

    # Run the command as a background process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        preexec_fn=create_process_group
    )
    print("Started Netstat Monitoring Loop process...")
    # Optional: Print the process ID (PID) if needed
    print("Process ID:", process.pid)
    return process
