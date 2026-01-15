#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import picamera2
import cv2


class Cameras:
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
        self.available_rpi_camera_models = []
        self.available_usb_camera_devices = []

    def configure(self):
        """ """

    def get_available_rpi_camera_models(self):
        """ """
        return self.available_rpi_camera_models

    def get_available_usb_camera_devices(self):
        """ """
        return self.available_usb_camera_devices

    def check_available_rpi_cameras(self):
        """ """
        self.available_rpi_camera_models = []
        global_camera_info = picamera2.Picamera2.global_camera_info()
        for index, camera_info in enumerate(global_camera_info):
            if "I2C" in camera_info.get("Id", "").upper():
                camera_model = camera_info.get("Model", "")
                self.available_rpi_camera_models.append(camera_model)

    def check_available_usb_cameras(self):
        """ """
        self.available_usb_camera_devices = []
        for device in [
            "/dev/video0",
            "/dev/video1",
            "/dev/video2",
            "/dev/video3",
            # "/dev/video4", # Don't use, conflict with RPi cam1.
        ]:
            try:
                capture = cv2.VideoCapture(device)
                try:
                    if capture.isOpened():
                        print("USB device: - Success: ", device)
                        self.available_usb_camera_devices.append(device)
                    else:
                        print("USB device: - Failed: ", device)
                finally:
                    capture.release()
                if len(self.available_usb_devices) >= 2:
                    break
            except Exception as e:
                self.logger.debug(
                    "Exception in Cameras - check_available_usb_cameras: " + str(e)
                )
