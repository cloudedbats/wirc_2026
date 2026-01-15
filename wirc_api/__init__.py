#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

from wirc_api.api_system import system_router
from wirc_api.api_camera import camera_router
from wirc_api.api_preview import preview_router
from wirc_api.api_directories import directories_router
from wirc_api.api_files import files_router

from wirc_api.html_camera import html_camera_router
from wirc_api.html_about import html_about_router

from wirc_api.api_main import app
