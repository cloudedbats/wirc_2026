#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import fastapi
import fastapi.templating
import wirc_core

logger = logging.getLogger(wirc_core.logger_name)
templates_path = pathlib.Path(wirc_core.workdir_path, "wirc_app/templates")
templates = fastapi.templating.Jinja2Templates(directory=templates_path)
html_about_router = fastapi.APIRouter()


@html_about_router.get(
    "/pages/about", tags=["HTML pages"], description="About page loaded as HTML."
)
async def load_about_page(request: fastapi.Request):
    """ """
    try:
        logger.debug("API called: module_about.")
        return templates.TemplateResponse(
            "about.html",
            {
                "request": request,
                "wurb_version": wirc_core.__version__,
            },
        )
    except Exception as e:
        message = "API - load_about_page. Exception: " + str(e)
        logger.debug(message)
