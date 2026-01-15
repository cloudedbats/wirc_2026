#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import fastapi
from fastapi.responses import StreamingResponse
import websockets.exceptions

import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

preview_router = fastapi.APIRouter()


async def preview_streamer_mjpeg(request, camera_id, fps):
    """ """
    # Calculate sleep for used fps.
    sleep_time_s = 0.2  # Use 5 fps as default.
    try:
        sleep_time_s = 1.0 / float(fps)
    except:
        pass

    preview_queue = None
    try:
        # Select preview queue.
        preview_queue = wirc_core.wirc_manager.get_preview_queue(camera_id)
        if preview_queue:
            while True:
                # Stop sending if client disconnected.
                if await request.is_disconnected():
                    break
                try:
                    # Wait for next frame. Timeout to check if disconnected.
                    preview_frame = await asyncio.wait_for(
                        preview_queue.get(),
                        timeout=1,
                    )
                    preview_queue.task_done()

                    # Use found frame.
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + preview_frame + b"\r\n"
                    )
                    # Sleep related to selected fps.
                    await asyncio.sleep(sleep_time_s)
                except asyncio.TimeoutError:
                    # Asyncio sleep needed to catch removed clients.
                    await asyncio.sleep(0)
    except asyncio.CancelledError:
        logger.debug("Preview client removed.")
    except websockets.exceptions.ConnectionClosed:
        logger.debug("Preview connection closed.")
    except Exception as e:
        logger.debug("Exception in mjpeg_streamer: " + str(e))


@preview_router.get(
    "/preview/stream.mjpeg",
    tags=["Preview"],
    description="Preview streamed as Motion JPEG.",
)
# async def stream_mjpeg(request: fastapi.Request):
async def preview_stream_mjpeg(
    request: fastapi.Request, camera_id: str = "camera-a", fps: str = "5"
):
    """ """
    try:
        logger.debug("API called: preview_stream_mjpeg.")
        return StreamingResponse(
            preview_streamer_mjpeg(request, camera_id, fps),
            media_type="multipart/x-mixed-replace;boundary=frame",
        )
    except websockets.exceptions.ConnectionClosed:
        logger.debug("Preview connection closed.")
    except Exception as e:
        message = "API - preview_stream_mjpeg. Exception: " + str(e)
        logger.debug(message)
