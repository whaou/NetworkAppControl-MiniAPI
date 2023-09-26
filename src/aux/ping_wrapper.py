
import pingparsing
from threading import Thread
import json
import aux.variables as variables
import re
import subprocess

PING_TIMEOUT = 5

class PingWrapperThread(Thread):
    def __init__(self, target, parser, transmitter):
        super().__init__()
        self.target = target
        self.parser = parser
        self.transmitter = transmitter
    
    def run(self):
       
        self.transmitter.destination = self.target
        self.transmitter.count = PING_TIMEOUT
        res = self.transmitter.ping()
        res = self.parser.parse(res).as_dict()
        with open(f'./static/{variables.E2E_RTT_RESULTS}', 'w') as json_file:
            json.dump(res, json_file)
        

def run_hping(self):
    host, port = self.host.split(":")
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
    except subprocess.CalledProcessError as e:
        print(f"Error running hping3: {e}")
        return None

def parse_hping_output(output):
    parsed_data = {
        "sent": None,
        "received": None,
        "loss": None,
        "min_rtt": None,
        "avg_rtt": None,
        "max_rtt": None,
    }

    # Regular expressions to extract relevant information from hping output
    sent_pattern = r"(\d+) packets transmitted"
    received_pattern = r"(\d+) packets received"
    loss_pattern = r"(\d+)% packet loss"
    rtt_pattern = r"min/avg/max = ([\d.]+)/([\d.]+)/([\d.]+) ms"

    # Extract data using regular expressions
    sent_match = re.search(sent_pattern, output)
    received_match = re.search(received_pattern, output)
    loss_match = re.search(loss_pattern, output)
    rtt_match = re.search(rtt_pattern, output)

    if sent_match:
        parsed_data["sent"] = int(sent_match.group(1))
    if received_match:
        parsed_data["received"] = int(received_match.group(1))
    if loss_match:
        parsed_data["loss"] = int(loss_match.group(1))
    if rtt_match:
        parsed_data["min_rtt"] = float(rtt_match.group(1))
        parsed_data["avg_rtt"] = float(rtt_match.group(2))
        parsed_data["max_rtt"] = float(rtt_match.group(3))

    return parsed_data