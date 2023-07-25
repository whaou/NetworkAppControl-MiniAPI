
import pingparsing
from threading import Thread
import json
import aux.variables as variables
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
        
        