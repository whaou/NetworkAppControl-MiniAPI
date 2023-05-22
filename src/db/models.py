# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 10:53:45
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-05-22 11:01:24
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from db.database import Base


class StreamConfig(Base):
    __tablename__ = "streamconfig"

    id = Column(Integer, primary_key=True, index=True)
    numberofStreams = Column(Integer)
    tputTotalDown = Column(Integer)
    tputTotalUp = Column(Integer)
