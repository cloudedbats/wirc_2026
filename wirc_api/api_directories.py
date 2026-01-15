#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import fastapi
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File
import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

directories_router = fastapi.APIRouter()


@directories_router.get(
    "/directories",
    tags=["Directories"],
    description="Get directories.",
)
async def get_directories():
    """ """
    try:
        logger.debug("API called: get_directories.")
        json_data = await wirc_core.wirc_files.get_directories()
        return JSONResponse(content=json_data)
    except Exception as e:
        message = "API - get_directories. Exception: " + str(e)
        logger.debug(message)


@directories_router.delete(
    "/directories",
    tags=["Directories"],
    description="Delete directory.",
)
async def delete_directory(dir_path: str):
    """ """
    try:
        logger.debug("API called: delete_directory.")
        json_data = await wirc_core.wirc_files.delete_directory(dir_path)
        return JSONResponse(content={"removed": True}, status_code=200)
    except FileNotFoundError:
        return JSONResponse(
            content={"removed": False, "error_message": "Directory not found."},
            status_code=404,
        )
    except Exception as e:
        message = "API - delete_directory. Exception: " + str(e)
        logger.debug(message)
