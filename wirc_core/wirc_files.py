#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import platform
import psutil
import datetime

import wirc_core


class WircFiles(object):
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
        self.camera_control_task = None
        self.base_dir_path = None

    def configure(self):
        """ """
        config = self.config
        # self.min_number_of_satellites = config.get(
        #     "gps_reader.min_number_of_satellites", 3
        # )
        self.source_dir = "/home/wurb/wirc_recordings"

    async def get_directories(self):
        """ """
        result = {}
        source_dir_path = pathlib.Path(self.source_dir)
        if source_dir_path:
            if source_dir_path.exists():
                for dir_path in source_dir_path.iterdir():
                    if dir_path.is_dir():
                        if str(dir_path.name) != "data":
                            dir_name = dir_path.name
                            dir_path = str(dir_path.resolve())
                            result[dir_name] = dir_path
        return result

    async def delete_directory(self, dir_path):
        """ """
        # TODO - delete_directory not implemented.
        raise FileNotFoundError("Delete not implemeted.")
        return {}

    async def get_files(self, dir_path, media_type=None):
        """ """
        video_files = {}
        if media_type in ["video", None]:
            video_files = await self.get_video_files(dir_path)
        return video_files

    async def get_video_files(self, dir_path):
        """ """
        result = {}
        if dir_path:
            dir_path = pathlib.Path(dir_path)
            for file_path in sorted(dir_path.glob("*.mp4")):
                file_name = file_path.name
                file_path = str(file_path.resolve())
                result[file_name] = file_path
        return result

    async def delete_file(self, file_path):
        """ """
        # TODO - delete_file not implemented.
        raise FileNotFoundError("Delete not implemeted.")
        return {}

    def get_target_disc_path(self):
        """
        Example from wurb_config_default.txt:
            record:
              targets:
                - id: sda1
                  name: USB-1
                  os: Linux
                  media_path: /media/USB-sda1
                  rec_dir: wirc_recordings
                - id: sdb1
                  name: USB-2
                  os: Linux
                  media_path: /media/USB-sdb1
                  rec_dir: wirc_recordings
                - id: local
                  name: Local
                  executable_path_as_base: true
                  rec_dir: ../wirc_recordings
                  free_disk_limit: 500 # Unit MB.

        Test examples for psutil.disk_usage:
            hdd = psutil.disk_usage(str(dir_path))
            total_disk = hdd.total / (2**20)
            used_disk = hdd.used / (2**20)
            free_disk = hdd.free / (2**20)
            percent_disk = hdd.percent
            print("Total disk: ", total_disk, "MB")
            print("Used disk: ", used_disk, "MB")
            print("Free disk: ", free_disk, "MB")
            print("Percent: ", percent_disk, "%")

        """

        # TEST:
        self.rec_targets = [
            {
                "id": "sda1",
                "name": "USB-1",
                "os": "Linux",
                "media_path": "/media/USB-sda1",
                "rec_dir": "wirc_recordings",
            },
            {
                "id": "sdb1",
                "name": "USB-2",
                "os": "Linux",
                "media_path": "/media/USB-sdb1",
                "rec_dir": "wirc_recordings",
            },
            {
                "id": "local",
                "name": "Local",
                "executable_path_as_base": True,
                "rec_dir": "../wirc_recordings",
                "free_disk_limit": 500,  # Unit MB.
            },
        ]

        try:
            platform_os = platform.system()  # Linux, Windows or Darwin (for macOS).
            used_dir_path = None
            # Check targets for recordings.
            for rec_target in self.rec_targets:
                if used_dir_path == None:
                    os = rec_target.get("os", "")
                    executable_path_as_base = rec_target.get(
                        "executable_path_as_base", False
                    )
                    media_path = rec_target.get("media_path", "")
                    rec_dir = rec_target.get("rec_dir", "")
                    free_disk_limit = rec_target.get("free_disk_limit", 100)  # Unit MB.
                    #
                    if executable_path_as_base:
                        base_path = pathlib.Path(wirc_core.executable_path)
                        used_dir_path = base_path
                    elif len(media_path) > 0:
                        if os in [platform_os, ""]:
                            # Directory may exist even when no USB attached.
                            # Use is_mount instead of exists on Linux.
                            media_path = pathlib.Path(media_path)
                            if platform_os == "Linux":
                                if media_path.is_mount():
                                    used_dir_path = media_path
                            else:
                                if media_path.exists():
                                    used_dir_path = media_path
                    else:
                        used_dir_path = pathlib.Path(".")

                    # Check if enough space is avaialble.
                    if used_dir_path != None:
                        hdd = psutil.disk_usage(str(used_dir_path))
                        free_disk = hdd.free / (2**20)  # To MB.
                        free_disk_limit = float(free_disk_limit)
                        if free_disk >= free_disk_limit:
                            # Return path.
                            return pathlib.Path(used_dir_path, rec_dir).resolve()

            message = "Not enough space left to store recordings."
            self.logger.error(message)
            return None
        except Exception as e:
            message = "Failed to find media for recordings. Exception: " + str(e)
            self.logger.debug(message)

        return None

    def get_target_dir_path(self, disc_path, date_option="date-post-before"):
        """ """
        target_directory = pathlib.Path(disc_path)
        file_directory = "WircStation"
        rec_target_dir = file_directory

        # date_option = wirc_core.wurb_settings.get_setting("fileDirectoryDateOption")

        used_date_str = ""
        if date_option in ["date-pre-true", "date-post-true"]:
            used_date = datetime.datetime.now()
            used_date_str = used_date.strftime("%Y-%m-%d")
        if date_option in ["date-pre-after", "date-post-after"]:
            used_date = datetime.datetime.now() + datetime.timedelta(hours=12)
            used_date_str = used_date.strftime("%Y-%m-%d")
        if date_option in ["date-pre-before", "date-post-before"]:
            used_date = datetime.datetime.now() - datetime.timedelta(hours=12)
            used_date_str = used_date.strftime("%Y-%m-%d")
        if date_option in ["date-pre-true", "date-pre-after", "date-pre-before"]:
            rec_target_dir = used_date_str + "_" + file_directory
        elif date_option in ["date-post-true", "date-post-after", "date-post-before"]:
            rec_target_dir = file_directory + "_" + used_date_str
        #
        self.rec_target_dir_path = pathlib.Path(target_directory, rec_target_dir)
        if not self.rec_target_dir_path.exists():
            self.rec_target_dir_path.mkdir(parents=True)

        return self.rec_target_dir_path
