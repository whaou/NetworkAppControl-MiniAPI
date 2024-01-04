
import subprocess
import aux.variables as variables
from aux.ping_wrapper import PingWrapperThread
import pingparsing
from aux.ping_wrapper import parse_hping_output
import json
import os
import multiprocessing

def create_process_group():
    os.setpgrp()

def start_iperf_client(target_ip, number_of_streams):
    
    command = f"iperf3 -t 5 -c {target_ip} -P {number_of_streams} -J > "\
    f"./static/{variables.E2E_SINGLE_UE_THROUGHPUT_AND_LATENCY}"

    # Run the command as a background process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    print(f"Started Iperf3 client process with {number_of_streams} streams...")
    # Optional: Print the process ID (PID) if needed
    print("Process ID:", process.pid)        
    return process

def start_iperf_server():
    # Command to start the iperf3 server
    command = "iperf3 -s"

    # Run the command as a background process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        preexec_fn=create_process_group
    )
    print(f"Started Iperf3 server process...")
    # Optional: Print the process ID (PID) if needed
    print("Process ID:", process.pid)        
    return process
    
def process_iperf_results(data):

    throughput_mbps = data['end']['sum_sent']['bits_per_second'] / 1000000
    
    mean_rtts_ms = []
    for stream in  data['end']["streams"]:
        mean_rtts_ms.append(stream["sender"]["mean_rtt"] * 0.001)

    mean_rtt_ms = sum(mean_rtts_ms)/len(mean_rtts_ms)

    return throughput_mbps, mean_rtt_ms


# todo: needs to be updated
def start_ping(target_ip, runs):
    
    for run in range(runs):
        command = f"ping -c 5 {target_ip} | grep time= | "\
            "awk '{print $7}' | cut -d'=' -f2 > "\
            f"./static/{variables.E2E_SINGLE_UE_LATENCY_BASE_NAME}_{i}.json"
        
        # Run the command as a background process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

    print(f"Started {runs} ping client processes ...")

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