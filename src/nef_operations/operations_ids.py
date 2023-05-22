# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 11:45:25
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-05-22 13:14:44

from enum import Enum
 
class NEF_OPERATION(Enum):
    LOGIN = 1
    CREATE_UE = 2
    GET_UES = 3
    SUBSCRIPTION = 4
    