# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 11:45:25
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-12-28 19:12:18

from enum import Enum
 
class OPERATION(Enum):
    ### NEF
    LOGIN = '1'
    CREATE_UE = '2'
    GET_UES = '3'
    SUBSCRIPTION = '4'
    UE_PATH_LOSS = '5'
    SERVING_CELL_INFO = '6'
    HANDOVER = '9'
    MAX_CONNECTIONS = "Def14Perf11"
    ### AVAILABILITY
    E2E_UE_PERFORMANCE = '7'
    E2E_UE_RTT_PERFORMANCE = '8'
