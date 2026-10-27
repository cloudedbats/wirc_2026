#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
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
        try:
            dev_v41_devices = []
            dir_path = pathlib.Path("/dev/v4l/by-id")
            if dir_path.exists():
                for path_by_id in dir_path.iterdir():
                    if path_by_id.is_symlink:
                        print("symlink")
                        print("path_by_id: ", path_by_id)
                        dev_v41_devices.append(path_by_id)

            for device_id in dev_v41_devices:
                # for device_index in [0, 1, 2, 3, 4, 5, 6]:
                # for device_index in ["/dev/video0", "/dev/video1"]:
                try:
                    symlink_value = str(device_id.resolve())
                    capture = cv2.VideoCapture(
                        symlink_value, apiPreference=cv2.CAP_V4L2
                    )
                    # capture = cv2.VideoCapture(device_id, apiPreference=cv2.CAP_V4L2)
                    try:
                        rc, image_array = capture.read()
                        if rc:
                            print("USB device: - Success: ", device_id.name)
                            # print("USB device: - Success: ", device_id)
                            self.available_usb_camera_devices.append(symlink_value)
                            capture.release()
                        else:
                            print("USB device: - Failed: ", device_id.name)
                            # print("USB device: - Failed: ", device_id)
                    finally:
                        pass
                        # capture.release()
                    if len(self.available_usb_camera_devices) >= 2:
                        break
                except Exception as e:
                    self.logger.debug(
                        "Exception in Cameras - check usb camera: " + str(e)
                    )
        except Exception as e:
            self.logger.debug(
                "Exception in Cameras - check_available_usb_cameras: " + str(e)
            )

    def release_usb_cameras(self):
        """ """
        for device_index in self.available_usb_camera_devices:
            try:
                capture = cv2.VideoCapture(device_index, apiPreference=cv2.CAP_V4L2)
                try:
                    capture.release()
                except Exception as e:
                    self.logger.debug(
                        "Exception in Cameras - release_usb_camera: " + str(e)
                    )
            except Exception as e:
                self.logger.debug(
                    "Exception in Cameras - release_usb_cameras: " + str(e)
                )
