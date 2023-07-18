
import subprocess
import aux.variables as variables
from aux.ping_wrapper import PingWrapperThread
import pingparsing

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