#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import uvicorn
import wirc_core
import wirc_utils


async def main():
    """ """
    # WIRC logger.
    wirc_utils.logger.setup_rotating_log(
        logger_name=wirc_core.logger_name,
        logging_dir=wirc_core.logging_dir,
        log_name=wirc_core.log_file_name,
        debug_log_name=wirc_core.debug_log_file_name,
    )
    logger = logging.getLogger(wirc_core.logger_name)
    logger.info("")
    logger.info("")
    logger.info("Welcome to CloudedBats WIRC-2026")
    logger.info("https://github.com/cloudedbats/wirc_2026")
    logger.info("================= ^ö^ ==================")
    logger.info("")

    try:
        # WIRC core startup.
        logger.debug("WIRC - main. Startup core.")
        await wirc_core.wirc_manager.startup()
        await asyncio.sleep(0)

        # API and app config.
        port = wirc_core.config.get("wirc_app.port", default="8082")
        port = int(port)
        host = wirc_core.config.get("wirc_app.host", default="0.0.0.0")
        log_level = wirc_core.config.get("wirc_app.log_level", default="info")

        logger.debug("WIRC - main. Uvicorn startup at port: " + str(port) + ".")
        config = uvicorn.Config(
            "wirc_api:app", loop="asyncio", host=host, port=port, log_level=log_level
        )

        # WIRC API and app startup.
        server = uvicorn.Server(config)
        await server.serve()

        # Shutdown actions.
        logger.debug("WIRC - main. Shutdown started.")
        await wirc_core.wirc_manager.shutdown()
        logger.debug("WIRC - main. Shutdown done.")
    except Exception as e:
        message = "WIRC - main. Exception: " + str(e)
        logger.error(message)


if __name__ == "__main__":
    """ """
    asyncio.run(main())
