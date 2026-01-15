#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import datetime
import logging
from logging import handlers

import wirc_core


class WircClientStatus:
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
        self.status_event = None
        self.cam0_exposure_time_us = None
        self.cam1_exposure_time_us = None
        self.cam0_camera_gain = None
        self.cam1_camera_gain = None

    def configure(self):
        """ """

    #     self.max_client_messages = self.config.get("client_info.max_log_rows", 10)

    def startup(self):
        """ """

    def shutdown(self):
        """ """
        if self.status_event:
            self.status_event.set()

    def set_exposure_time_us(self, exposure_time_us, camera_id="camera-a"):
        """ """
        if camera_id == "camera-a":
            self.cam0_exposure_time_us = exposure_time_us
            self.trigger_status_event()
        if camera_id == "camera-b":
            self.cam1_exposure_time_us = exposure_time_us
            self.trigger_status_event()

    def set_camera_gain(self, camera_gain, camera_id="camera-a"):
        """ """
        if camera_id == "camera-a":
            self.cam0_camera_gain = camera_gain
            self.trigger_status_event()
        if camera_id == "camera-b":
            self.cam1_camera_gain = camera_gain
            self.trigger_status_event()

    def trigger_status_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_status_event()
        self.status_event = asyncio.Event()
        old_event.set()

    def get_status_event(self):
        """ """
        if self.status_event == None:
            self.status_event = asyncio.Event()
        return self.status_event

    def get_camera_status_all(self):
        """ """
        camera_status_dict = {}
        camera_status_dict["camera-a"] = wirc_core.rpi_cam0.get_camera_status()
        camera_status_dict["camera-b"] = wirc_core.rpi_cam1.get_camera_status()
        camera_status_dict["camera-c"] = wirc_core.usb_cam0.get_camera_status()
        camera_status_dict["camera-d"] = wirc_core.usb_cam1.get_camera_status()
        return camera_status_dict
