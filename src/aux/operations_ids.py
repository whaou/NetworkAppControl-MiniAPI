# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 11:45:25
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-05-22 13:14:44

from enum import Enum
 
class OPERATION(Enum):
    ### NEF
    LOGIN = 1
    CREATE_UE = 2
    GET_UES = 3
    SUBSCRIPTION = 4
    UE_PATH_LOSS = 5
    SERVING_CELL_INFO = 6
    ### AVAILABILITY
    E2E_UE_PERFORMANCE = 7
