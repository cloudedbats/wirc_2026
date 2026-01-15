#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import os
import datetime
import pathlib


class RaspberryPiControl(object):
    """ """

    def __init__(self, logger=None, logger_name="DefaultLogger"):
        """ """
        self.logger = logger
        if self.logger == None:
            self.logger = logging.getLogger(logger_name)
        #
        self.clear()

    def clear(self):
        """ """
        self.os_debian = None

    async def rpi_control(self, command):
        """ """
        try:
            # First check: Debian. Only valid for Debian OS.
            if self.is_os_debian():
                # Select command.
                if command == "rpiShutdown":
                    await self.rpi_shutdown()
                elif command == "rpiReboot":
                    await self.rpi_reboot()
                elif command == "rpi_sd_to_usb":
                    await self.rpi_sd_to_usb()
                # elif command == "rpi_clear_sd_ok":
                elif command == "rpi_clear_sd":
                    await self.rpi_clear_sd()
                else:
                    # Logging.
                    message = (
                        "Raspberry Pi command failed. Not a valid command: " + command
                    )
                    self.logger.error(message)
            else:
                # Logging.
                message = (
                    "Raspberry Pi command failed (" + command + "), not Debian OS."
                )
                self.logger.warning(message)
        except Exception as e:
            message = "RaspberryPi - rpi_control. Exception: " + str(e)
            self.logger.debug(message)

    async def set_detector_time(self, posix_time_s, cmd_source=""):
        """Only valid for Debian and user wurb."""
        try:
            local_datetime = datetime.datetime.fromtimestamp(posix_time_s)
            # utc_datetime = datetime.datetime.utcfromtimestamp(posix_time_s)
            # local_datetime = utc_datetime.replace(
            #     tzinfo=datetime.timezone.utc
            # ).astimezone(tz=None)
            time_string = local_datetime.strftime("%Y-%m-%d %H:%M:%S")
            print(time_string)
            # Logging.
            message = "Detector time update: " + time_string
            if cmd_source:
                message += " (" + cmd_source + ")."
            self.logger.info(message)
            # First check: OS Raspbian.
            if self.is_os_debian():
                # Second check: User wurb exists. Perform: "date --set".
                os.system('cd /home/wurb && sudo date --set "' + time_string + '"')
            else:
                # Logging.
                message = "Detector time update failed, not Debian OS."
                self.logger.warning(message)
        except Exception as e:
            message = "RaspberryPi - set_detector_time. Exception: " + str(e)
            self.logger.debug(message)

    def is_os_debian(self):
        """Check OS version for Raspberry Pi."""
        try:
            if self.os_debian is not None:
                return self.os_debian
            else:
                try:
                    os_version_path = pathlib.Path("/etc/os-release")
                    if os_version_path.exists():
                        with os_version_path.open("r") as os_file:
                            os_file_content = os_file.read()
                            # print("Content of /etc/os-release: ", os_file_content)
                            if "DEBIAN" in os_file_content.upper():
                                self.os_debian = True
                            else:
                                self.os_debian = False
                    else:
                        self.os_debian = False
                except Exception as e:
                    message = "RaspberryPi - is_os_debian. Exception: " + str(e)
                    self.logger.debug(message)
            #
            return self.os_debian
        except Exception as e:
            message = "RaspberryPi - is_os_debian. Exception: " + str(e)
            self.logger.debug(message)
            self.os_debian = None
            return self.os_debian

    async def rpi_shutdown(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Shutdown' is activated."
            self.logger.info(message)
            await asyncio.sleep(1.0)
            #
            os.system("cd /home/wurb && sudo shutdown -h now")
        except Exception as e:
            message = "RaspberryPi - rpi_shutdown. Exception: " + str(e)
            self.logger.debug(message)

    async def rpi_reboot(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Reboot' is activated."
            self.logger.info(message)
            await asyncio.sleep(1.0)
            #
            os.system("cd /home/wurb && sudo reboot")
        except Exception as e:
            message = "RaspberryPi - rpi_reboot. Exception: " + str(e)
            self.logger.debug(message)

    async def rpi_sd_to_usb(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Copy SD to USB' is not implemented."
            self.logger.info(message)
        except Exception as e:
            message = "RaspberryPi - rpi_sd_to_usb. Exception: " + str(e)
            self.logger.debug(message)

    async def rpi_clear_sd(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Clear SD card' is not implemented."
            self.logger.info(message)
        except Exception as e:
            message = "RaspberryPi - rpi_clear_sd. Exception: " + str(e)
            self.logger.debug(message)
