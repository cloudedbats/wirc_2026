#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import datetime

import wirc_core


class WircManager(object):
    """ """

    def __init__(self, config={}, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()

    def clear(self):
        """ """
        self.rpi_cam0_active = False
        self.rpi_cam1_active = False
        self.usb_cam0_active = False
        self.usb_cam1_active = False

    def configure(self):
        """ """
        config = self.config

    def _select_camera(self, camera_id="camera-a"):
        """ """
        rpicam = None
        if camera_id == "camera-a":
            if self.rpi_cam0_active == True:
                rpicam = wirc_core.rpi_cam0
        elif camera_id == "camera-b":
            if self.rpi_cam1_active == True:
                rpicam = wirc_core.rpi_cam1
        elif camera_id == "camera-c":
            if self.usb_cam0_active == True:
                rpicam = wirc_core.usb_cam0
        elif camera_id == "camera-d":
            if self.usb_cam1_active == True:
                rpicam = wirc_core.usb_cam1
        return rpicam

    def get_preview_queue(self, camera_id="camera-a"):
        """ """
        rpicam = self._select_camera(camera_id)
        if rpicam:
            return rpicam.preview_queue
        return None

    async def camera_mode(self, camera_id, camera_mode):
        """ """
        rpicam = self._select_camera(camera_id)
        if rpicam:
            await rpicam.set_camera_mode(camera_mode)
            message = camera_id.capitalize() + ": " + camera_mode + "."
            wirc_core.client_info.write_log("info", message)
        wirc_core.client_status.trigger_status_event()

    async def camera_trigger(self, camera_id):
        """ """
        rpicam = self._select_camera(camera_id)
        if rpicam:
            await rpicam.camera_trigger()
            message = camera_id.capitalize() + ": triggered."
            wirc_core.client_info.write_log("info", message)
        wirc_core.client_status.trigger_status_event()

    async def set_saturation(self, saturation, camera_id="rpi-cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        if rpicam:
            await rpicam.set_camera_controls(saturation=saturation)
        wirc_core.client_status.trigger_status_event()

    async def set_exposure_time(self, camera_id, exposure_time_us):
        """ """
        rpicam = self._select_camera(camera_id)
        if rpicam:
            await rpicam.set_camera_controls(exposure_time_us=exposure_time_us)
        wirc_core.client_status.trigger_status_event()

    async def set_camera_gain(self, camera_id, camera_gain):
        """ """
        rpicam = self._select_camera(camera_id)
        if rpicam:
            await rpicam.set_camera_controls(camera_gain=camera_gain)
        wirc_core.client_status.trigger_status_event()

    def log_camera_info(self):
        """ """
        status = wirc_core.usb_cam1.get_camera_status()
        device = status.get("camera_device_name", None)
        if device:
            message = "Camera-D (usb1)   device: " + device + "."
            wirc_core.client_info.write_log("info", message)
        status = wirc_core.usb_cam0.get_camera_status()
        device = status.get("camera_device_name", None)
        if device:
            message = "Camera-C (usb0)   device: " + device + "."
            wirc_core.client_info.write_log("info", message)
        status = wirc_core.rpi_cam1.get_camera_status()
        model = status.get("camera_model", None)
        if model:
            message = "Camera-B (cam1)   model: " + model + "."
            wirc_core.client_info.write_log("info", message)
        status = wirc_core.rpi_cam0.get_camera_status()
        model = status.get("camera_model", None)
        if model:
            message = "Camera-A (cam0)   model: " + model + "."
            wirc_core.client_info.write_log("info", message)

    async def startup(self):
        """ """
        # config = self.config
        try:
            wirc_core.cameras.check_available_rpi_cameras()
            wirc_core.cameras.check_available_usb_cameras()
            rpi_cameras = wirc_core.cameras.get_available_rpi_camera_models()
            usb_cameras = wirc_core.cameras.get_available_usb_camera_devices()
            if len(rpi_cameras) >= 1:
                self.rpi_cam0_active = True
                wirc_core.rpi_cam0.set_camera_model(rpi_cameras[0])
            if len(rpi_cameras) >= 2:
                self.rpi_cam1_active = True
                wirc_core.rpi_cam1.set_camera_model(rpi_cameras[1])
            if len(usb_cameras) >= 1:
                self.usb_cam0_active = True
                wirc_core.usb_cam0.set_camera_device_name(usb_cameras[0])
            if len(usb_cameras) >= 2:
                self.usb_cam1_active = True
                wirc_core.usb_cam1.set_camera_device_name(usb_cameras[1])

            self.log_camera_info()
        except Exception as e:
            self.logger.debug("Exception in WircManager - startup: " + str(e))

    async def shutdown(self):
        """ """
        try:
            pass
            # await wirc_core.rpi_cam0.set_camera_mode("camera-off")
            # await wirc_core.rpi_cam1.set_camera_mode("camera-off")
            # await wirc_core.usb_cam0.set_camera_mode("camera-off")
            # await wirc_core.usb_cam1.set_camera_mode("camera-off")
        except Exception as e:
            self.logger.debug("Exception in WircManager - shutdown: " + str(e))
