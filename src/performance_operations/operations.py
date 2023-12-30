
import subprocess
import aux.variables as variables
from aux.ping_wrapper import PingWrapperThread
import pingparsing
from aux.ping_wrapper import parse_hping_output
import json
import os
import multiprocessing

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


def compute_max_hops(target):
    max_hops=30
    for ttl in range(1, max_hops + 1):
        print(f"TTL: {ttl}")
        response = os.system(f"ping -c 3 -t {ttl} {target} > /dev/null")
        if response == 0:
            print(f"Reached {target} with {ttl} hops!")
            with open(
                f'./static/{variables.MAX_HOPS_RESULTS}',
                'w'
            ) as json_file:
                json.dump(
                    {
                        target: {
                            "hops_until_target": ttl
                        }
                    },
                    json_file
                )
            return
        print(
            f"Could not reach {target} with {ttl} hops. Will try with "
            f"{ttl + 1} hops..."
        )
    
    # Finally, create an output file for the unsuccessful test cases
    with open(
        f'./static/{variables.MAX_HOPS_RESULTS}',
        'w'
    ) as json_file:
        json.dump(
            {
                target: {
                    "hops_until_target": -1
                }
            },
            json_file
        )


def start_max_hops_computing(target):
    print(f"Will compute the number of hops until the target {target}...")
    # Run the command as a background process
    process = multiprocessing.Process(
        target=compute_max_hops,
        args=(target,)
    )
    process.start()
    print("Started the hops computation process...")
    # Optional: Print the process ID (PID) if needed
    print("Process ID:", process.pid)
    return process