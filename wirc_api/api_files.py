#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib

import fastapi
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File
import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

files_router = fastapi.APIRouter()


@files_router.get(
    "/files",
    tags=["Files"],
    description="Get files in directory.",
)
async def get_files(dir_path: str, media_type: str = None):
    """ """
    try:
        logger.debug("API called: get_files.")
        json_data = await wirc_core.wirc_files.get_files(
            dir_path, media_type=media_type
        )
        return JSONResponse(content=json_data)
    except Exception as e:
        message = "API - get_files. Exception: " + str(e)
        logger.debug(message)


@files_router.get(
    "/files/download",
    tags=["Files"],
    description="Get file for download.",
)
async def download_file(file_path: str):
    """ """
    try:
        logger.debug("API called: download_file.")
        file_path = pathlib.Path(file_path)
        file_name = file_path.name
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=file_name,
        )
    except Exception as e:
        message = "API - download_file. Exception: " + str(e)
        logger.debug(message)


@files_router.delete(
    "/files",
    tags=["Files"],
    description="Delete file.",
)
async def delete_file(file_path: str):
    """ """
    try:
        logger.debug("API called: delete_file.")
        json_data = await wirc_core.wirc_files.delete_file()
        return JSONResponse(content={"removed": True}, status_code=200)
    except FileNotFoundError:
        return JSONResponse(
            content={"removed": False, "error_message": "Selected file not found."},
            status_code=404,
        )
    except Exception as e:
        message = "API - delete_file. Exception: " + str(e)
        logger.debug(message)
