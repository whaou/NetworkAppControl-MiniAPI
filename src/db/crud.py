# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 10:53:45
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-05-22 11:02:31
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from db import models
from schemas import types as schemas


def get_stream_config(db: Session, stream_config_id: int):
    return db.query(models.StreamConfig).filter(models.StreamConfig.id == stream_config_id).first()

def get_stream_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.StreamConfig).offset(skip).limit(limit).all()


def create_stream_config(db: Session, stream_config: schemas.StreamConfig):
    db_stream_config = models.StreamConfig(numberofStreams = stream_config["numberofStreams"], tputTotalDown = stream_config["tputTotalDown"], tputTotalUp = stream_config["tputTotalUp"])
    db.add(db_stream_config)
    db.commit()
    db.refresh(db_stream_config)
    return db_stream_config
