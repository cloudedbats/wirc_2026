#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import fastapi
import pydantic
from fastapi.responses import StreamingResponse
import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

camera_router = fastapi.APIRouter()


class CameraMode(pydantic.BaseModel):
    camera_id: str
    camera_mode: str


@camera_router.post(
    "/camera/camera-mode/",
    tags=["Cameras"],
    description="Commands to stop, start and restart.",
)
async def camera_mode(params: CameraMode):
    """ """
    try:
        logger.debug(
            "API called: camera_mode: "
            + params.camera_mode
            + " for "
            + params.camera_id
        )
        await wirc_core.wirc_manager.camera_mode(params.camera_id, params.camera_mode)
        await asyncio.sleep(0)
    except Exception as e:
        message = "Exception: API - camera_mode" + str(e)
        logger.debug(message)


class CameraExpTime(pydantic.BaseModel):
    camera_id: str
    exposure_time_us: str


@camera_router.post(
    "/camera/exposure-time/",
    tags=["Cameras"],
    description="Set exposure time.",
)
async def set_exposure_time(params: CameraExpTime):
    """ """
    try:
        logger.debug("API called: set_exposure_time.")
        await wirc_core.wirc_manager.set_exposure_time(
            params.camera_id, params.exposure_time_us
        )
    except Exception as e:
        message = "API - set_exposure_time. Exception: " + str(e)
        logger.debug(message)


class CameraGain(pydantic.BaseModel):
    camera_id: str
    camera_gain: str


@camera_router.post(
    "/camera/camera-gain/",
    tags=["Cameras"],
    description="Set camera gain.",
)
async def set_camera_gain(params: CameraGain):
    """ """
    try:
        logger.debug("API called: set_camera_gain.")
        await wirc_core.wirc_manager.set_camera_gain(
            params.camera_id, params.camera_gain
        )
    except Exception as e:
        message = "API - set_camera_gain. Exception: " + str(e)
        logger.debug(message)
