#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import pathlib
import logging
import io
from picamera2 import Picamera2, encoders, outputs, Metadata
import libcamera
from datetime import datetime, timedelta

import wirc_core


class RaspberryPiCamera:
    """ """

    def __init__(
        self,
        config={},
        logger_name="DefaultLogger",
        config_id="rpi-cam0",
        camera_name="Camera-A",
    ):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.camera_initiated = False
        self.config_id = config_id
        self.camera_name = camera_name
        self.configure()
        # For preview streaming.
        self.preview_queue = asyncio.Queue(maxsize=10)
        self.preview_streamer = PreviewStreamingOutput()
        self.preview_streamer.set_preview_queue(self.preview_queue)
        # Trigger.
        self.video_trigger_event = None

    def clear(self):
        """ """
        self.camera_mode = "camera-off"
        self.preview_mode = "preview-off"
        self.picam2 = None
        self.video_configuration = None
        self.sensor_modes = None
        self.sensor_resolution = None
        self.camera_properties = None
        self.camera_controls = None
        #
        self.preview_encoder = None
        self.video_active = False
        self.video_task = None
        self.trigger_video_active = False
        self.trigger_video_task = None
        self.camera_info = ""
        self.camera_model = None

    def configure(self):
        """ """
        conf = self.config
        cam = self.config_id
        #
        self.rpi_camera_id = self.config_id
        self.startup_mode = conf.get(cam + ".settings.startup_mode", False)
        self.colour = conf.get(cam + ".settings.colour", False)
        self.saturation = conf.get(cam + ".settings.saturation", "auto")
        self.exposure_time_us = conf.get(cam + ".settings.exposure_time_us", "auto")
        self.camera_gain = conf.get(cam + ".settings.camera_gain", "auto")
        self.hflip = conf.get(cam + ".orientation.hflip", 0)
        self.vflip = conf.get(cam + ".orientation.vflip", 0)
        self.preview_size_divisor = conf.get(cam + ".preview.size_divisor", 2.0)
        self.video_horizontal_size_px = conf.get(
            cam + ".video.horizontal_size_px", "max"
        )
        self.video_vertical_size_px = conf.get(cam + ".video.vertical_size_px", "auto")
        self.video_framerate_fps = conf.get(cam + ".video.framerate_fps", 30)
        self.video_pre_buffer_frames = conf.get(cam + ".video.pre_buffer_frames", 30)

        self.directory_name = conf.get(cam + ".video.directory_name", "WircStation")
        self.date_option = conf.get(cam + ".video.date_option", "date-post-before")
        self.file_prefix = conf.get(cam + ".video.file_prefix", self.camera_name)

        self.camera_info = "Config id: " + self.config_id + "."

    def set_camera_model(self, camera_model):
        """ """
        self.camera_model = camera_model

    def get_camera_status(self):
        """ """
        camera_status = {}
        camera_status["camera_model"] = self.camera_model
        camera_status["camera_mode"] = self.camera_mode
        camera_status["preview_mode"] = self.preview_mode
        camera_status["exposure_time_us"] = self.exposure_time_us
        camera_status["camera_gain"] = self.camera_gain
        camera_status["video_framerate_fps"] = self.video_framerate_fps
        camera_status["camera_info"] = self.camera_info
        return camera_status

    async def set_camera_mode(self, camera_mode=None, preview_mode=None):
        """ """
        old_camera_mode = self.camera_mode
        old_preview_mode = self.preview_mode
        if (old_camera_mode == camera_mode) and (old_preview_mode == preview_mode):
            return

        self.camera_mode = camera_mode
        self.preview_mode = preview_mode
        if camera_mode == None:
            self.camera_mode = self.startup_mode
        if preview_mode == None:
            self.preview_mode = "preview-off"
        #
        if self.camera_mode == "camera-off":
            self.preview_mode = "preview-off"
            if self.picam2 != None:
                await self.stop_camera()
                await asyncio.sleep(0)
            return

        if self.camera_mode in ["camera-on", "record-on", "record-on-trigger"]:
            if self.picam2 == None:
                await self.initiate_camera()
                await asyncio.sleep(0)

        if self.preview_mode == "preview-off":
            await self.stop_preview()
            await asyncio.sleep(0)
        else:
            await self.start_preview(preview_mode)
            await asyncio.sleep(0)

        if self.camera_mode == old_camera_mode:
            return

        if self.camera_mode in ["camera-on", "record-on", "record-on-trigger"]:
            await self.stop_video()
            await asyncio.sleep(0)
            await self.stop_trigger_video()
            await asyncio.sleep(0)

        if self.camera_mode == "record-on":
            await self.start_video()
            await asyncio.sleep(0)

        if self.camera_mode == "record-on-trigger":
            await self.start_trigger_video()
            await asyncio.sleep(0)

        message = self.camera_name + ": " + str(self.camera_mode) + "."
        wirc_core.client_info.write_log("info", message)

    async def video_trigger(self):
        """ """
        self.trigger_video_trigger_event()

    async def initiate_camera(self):
        """ """
        if self.camera_initiated == True:
            return

        self.camera_initiated = True
        # Camera.
        await self.camera_setup()
        await asyncio.sleep(0)
        # Configure for video and preview from setup.
        self.picam2.configure(self.video_configuration)
        # Controls.
        await self.config_camera_controls()
        await asyncio.sleep(0)
        self.picam2.start()
        await asyncio.sleep(0)

    async def stop_camera(self):
        """ """
        self.preview_mode = "preview-off"
        self.camera_initiated = False
        try:
            # Preview encoders.
            await self.stop_preview()
            await asyncio.sleep(0)
            await self.stop_video()
            await asyncio.sleep(0)
            await self.stop_trigger_video()
            await asyncio.sleep(0)
            # Camera.
            self.picam2.close()
            self.picam2 = None
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_camera: " + str(e))

    async def start_preview(self, preview_mode=None):
        """ """
        if self.preview_encoder != None:
            await self.stop_preview()
            # return
        try:
            # Setup preview stream.
            self.preview_encoder = encoders.MJPEGEncoder()
            # Reduce preview frame speed.
            if preview_mode:
                skip_count = 0
                fps = int(self.video_framerate_fps)
                if preview_mode == "preview-on":
                    pass
                elif preview_mode == "preview-10-fps":
                    if fps >= 10:
                        skip_count = int(fps * 0.1)
                elif preview_mode == "preview-5-fps":
                    if fps >= 5:
                        skip_count = int(fps * 0.2)
                elif preview_mode == "preview-2-fps":
                    if fps >= 2:
                        skip_count = int(fps * 0.5)
                elif preview_mode == "preview-1-fps":
                    if fps >= 1:
                        skip_count = int(fps)
                elif preview_mode == "preview-0.1-fps":
                    skip_count = int(fps * 10.0)
                #
                print("DEBUG: Skip-count: ", skip_count)
                if skip_count > 1:
                    self.preview_encoder.frame_skip_count = skip_count

            self.preview_encoder.output = outputs.FileOutput(self.preview_streamer)
            self.picam2.start_encoder(
                self.preview_encoder, name="lores", quality=encoders.Quality.LOW
            )
            await asyncio.sleep(0)

        except Exception as e:
            self.logger.debug("Exception in start_preview: " + str(e))

    async def stop_preview(self):
        """ """
        if self.preview_encoder == None:
            return
        try:
            try:
                self.picam2.stop_encoder(self.preview_encoder)
                # self.preview_encoder.output.stop()
                # await asyncio.sleep(0)
                # if self.preview_encoder and self.preview_encoder.running:
                #     self.preview_encoder.stop()
            finally:
                self.preview_encoder = None
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_preview: " + str(e))

    async def camera_setup(self):
        """ """
        try:
            # Close if already running.
            if self.picam2 != None:
                try:
                    await self.stop_preview()
                except:
                    pass
            # Create a new camera object, cam0 or cam1.
            camera_index = 0
            if self.rpi_camera_id == "rpi-cam1":
                camera_index = 1
            try:
                self.picam2 = Picamera2(camera_num=camera_index)
            except Exception as e:
                self.logger.debug("Exception in camera_setup: " + str(e))
                self.picam2 = None
                return
            # Generic info...
            self.sensor_modes = self.picam2.sensor_modes
            self.sensor_resolution = self.picam2.sensor_resolution
            self.camera_properties = self.picam2.camera_properties
            self.camera_controls = self.picam2.camera_controls
            # ...to debug log.
            message = "Sensor modes (" + str(camera_index) + "): "
            message += str(self.sensor_modes)
            self.logger.debug(message)
            message = "Sensor resolution (" + str(camera_index) + "): "
            message += str(self.sensor_resolution)
            self.logger.debug(message)
            message = "Camera properties (" + str(camera_index) + "): "
            message += str(self.camera_properties)
            self.logger.debug(message)
            message = "Camera controls (" + str(camera_index) + "): "
            message += str(self.camera_controls)
            self.logger.debug(message)
            # Keep the aspect ratio from the sensor.
            max_resolution = self.sensor_resolution  # RPi-GC: (1456, 1088).
            size_factor = max_resolution[0] / max_resolution[1]
            if self.video_horizontal_size_px in ["max", "auto"]:
                main_width = int(max_resolution[0])
            else:
                main_width = int(self.video_horizontal_size_px)
            if self.video_vertical_size_px in ["max", "auto"]:
                main_height = int(main_width / size_factor)
            else:
                main_height = int(self.video_vertical_size_px)
            lores_width = int(main_width / self.preview_size_divisor)
            lores_height = int(main_height / self.preview_size_divisor)

            # Define video configuration.
            self.video_configuration = self.picam2.create_video_configuration(
                main={"size": (main_width, main_height)},
                lores={"size": (lores_width, lores_height)},
                transform=libcamera.Transform(hflip=self.hflip, vflip=self.vflip),
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in camera_setup: " + str(e))

    async def config_camera_controls(self):
        """ """
        try:
            await self.set_camera_controls(
                self.exposure_time_us,
                self.camera_gain,
                self.saturation,
                self.video_framerate_fps,
            )

            # print(
            #     "DEBUG: self.picam2.controls.AeEnable: " + str(self.picam2.camera_controls["AeEnable"])
            # )
            self.picam2.set_controls({"AeEnable": False})
            # self.picam2.controls.AeEnable = False

            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in config_camera_controls: " + str(e))

    async def set_camera_controls(
        self,
        exposure_time_us=None,
        camera_gain=None,
        saturation=None,
        video_framerate_fps=None,
    ):
        """ """
        if self.picam2 == None:
            return

        try:
            if exposure_time_us != None:
                self.exposure_time_us = exposure_time_us
                if exposure_time_us == "auto":
                    exposure_time_us = 0
                try:
                    self.picam2.controls.ExposureTime = int(exposure_time_us)
                except:
                    pass
            if camera_gain != None:
                self.camera_gain = camera_gain
                if camera_gain == "auto":
                    camera_gain = 0
                try:
                    self.picam2.controls.AnalogueGain = int(camera_gain)
                except:
                    pass
            if saturation != None:
                if self.colour == True:
                    if saturation == "auto":
                        saturation = 1.0
                    try:
                        self.picam2.controls.Saturation = float(saturation)
                    except:
                        pass
                else:
                    try:
                        self.picam2.controls.Saturation = 0.0
                    except:
                        pass
            if video_framerate_fps != None:
                self.video_framerate_fps = video_framerate_fps
                if video_framerate_fps == "auto":
                    video_framerate_fpsframerate_fps = 30
                try:
                    self.picam2.controls.FrameRate = int(video_framerate_fps)
                except:
                    pass

            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in set_camera_controls: " + str(e))

    async def start_video(self):
        """ """
        try:
            if self.video_active == True:
                print("DEBUG: Video is already running.")
                return

            self.video_active = True
            self.video_task = asyncio.create_task(
                self._video_loop(), name="Camera video loop"
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        try:
            if self.video_active == True:
                self.video_task.cancel()
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))

    async def _video_loop(self):
        """ """
        self.video_active = True
        out_path = ""
        try:
            try:
                # Decoder and output for video.
                self.video_encoder = encoders.H264Encoder()
                self.video_output = None
                next_time_minute = None
                await asyncio.sleep(0)

                while True:
                    now = datetime.now()
                    date_and_time = now.strftime("%Y%m%dT%H%M%S")
                    file_mp4_name = self.file_prefix + "_" + date_and_time + ".mp4"

                    disc_path = wirc_core.wirc_files.get_target_disc_path()
                    dir_path = wirc_core.wirc_files.get_target_dir_path(
                        disc_path,
                        directory_name=self.directory_name,
                        date_option=self.date_option,
                    )
                    video_mp4_path = pathlib.Path(dir_path, file_mp4_name)

                    try:
                        metadata = Metadata(self.picam2.capture_metadata())
                        exposure = metadata.ExposureTime
                        gain = metadata.AnalogueGain
                        exposure = int(round(1000000 / exposure, 0))
                        gain = round(gain, 1)
                        metadata_string = "exp" + str(exposure) + "-gain" + str(gain)
                        self.logger.debug(
                            "Exposure time: 1/"
                            + str(exposure)
                            + " sec, gain: "
                            + str(gain)
                        )
                        out_path = str(video_mp4_path).replace(
                            ".mp4", "_" + metadata_string + ".mp4"
                        )

                        message = self.camera_name + ": Video: " + str(out_path)
                        wirc_core.client_info.write_log("info", message)

                        if self.video_output == None:
                            self.video_output = outputs.PyavOutput(out_path)
                            self.video_encoder.output = [self.video_output]
                            self.picam2.start_encoder(
                                self.video_encoder, quality=encoders.Quality.LOW
                            )
                        else:
                            self.picam2.stop_encoder(self.video_encoder)
                            self.video_output = outputs.PyavOutput(out_path)
                            self.video_encoder.output = [self.video_output]
                            self.picam2.start_encoder(
                                self.video_encoder, quality=encoders.Quality.LOW
                            )

                        next_time = now + timedelta(seconds=60)
                        next_time_minute = next_time.replace(
                            second=0,
                            microsecond=0,
                            minute=next_time.minute,
                            hour=next_time.hour,
                        )
                        time_left = next_time_minute - datetime.now()
                        time_left_sec = time_left.total_seconds()
                        await asyncio.sleep(time_left_sec)

                    except Exception as e:
                        self.logger.debug("Exception in _video_loop: " + str(e))

            finally:
                self.picam2.stop_encoder(self.video_encoder)
                await asyncio.sleep(0)
                message = self.camera_name + ": Video: " + str(out_path)
                wirc_core.client_info.write_log("info", message)
                await asyncio.sleep(0)

        except Exception as e:
            self.logger.debug("Exception in _video_loop: " + str(e))

        finally:
            # Release.
            self.video_active = False
            self.logger.debug("_video_loop ended.")

    async def start_trigger_video(self):
        """ """
        try:
            if self.trigger_video_active == True:
                print("DEBUG: Video (trigger) is already running.")
                return

            self.trigger_video_active = True
            self.trigger_video_task = asyncio.create_task(
                self._trigger_video_loop(), name="Camera trigger video loop"
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_trigger_video(self):
        """ """
        try:
            if self.trigger_video_active == True:
                self.trigger_video_task.cancel()
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))

    async def _trigger_video_loop(self):
        """ """
        self.trigger_video_active = True
        out_path = ""
        next_time_minute = None

        pre_trigger_s = 2.0
        post_trigger_s = 4.0

        try:
            try:
                # Decoder and output for trigger_video.
                self.trigger_video_encoder = encoders.H264Encoder()
                self.trigger_video_output = outputs.CircularOutput2(
                    buffer_duration_ms=int(pre_trigger_s * 1000.0)
                )
                # Start the circular output.
                self.picam2.start_encoder(
                    self.trigger_video_encoder,
                    self.trigger_video_output,
                    name="main",
                    quality=encoders.Quality.LOW,
                    # quality=encoders.Quality.VERY_LOW,
                )
                # Get trigger event.
                video_trigger_event = self.get_video_trigger_event()
                await asyncio.sleep(0)

                while True:

                    # Wait until trigger event is set.
                    await video_trigger_event.wait()
                    # Used for next trigger events.
                    video_trigger_event = self.get_video_trigger_event()

                    now = datetime.now() - timedelta(seconds=pre_trigger_s - 0.5)
                    date_and_time = now.strftime("%Y%m%dT%H%M%S")
                    file_mp4_name = (
                        self.file_prefix + "_" + date_and_time + ".mp4"
                    )

                    disc_path = wirc_core.wirc_files.get_target_disc_path()
                    dir_path = wirc_core.wirc_files.get_target_dir_path(
                        disc_path,
                        directory_name=self.directory_name,
                        date_option=self.date_option,
                    )
                    trigger_video_mp4_path = pathlib.Path(dir_path, file_mp4_name)

                    try:
                        metadata = Metadata(self.picam2.capture_metadata())
                        exposure = metadata.ExposureTime
                        gain = metadata.AnalogueGain
                        exposure = int(round(1000000 / exposure, 0))
                        gain = round(gain, 1)
                        metadata_string = "exp" + str(exposure) + "-gain" + str(gain)
                        self.logger.debug(
                            "Exposure time: 1/"
                            + str(exposure)
                            + " sec, gain: "
                            + str(gain)
                        )
                        out_path = str(trigger_video_mp4_path).replace(
                            ".mp4", "_" + metadata_string + "_TRIGGER.mp4"
                        )

                        message = self.camera_name + ": Trigger video: " + str(out_path)
                        wirc_core.client_info.write_log("info", message)

                        self.trigger_video_output.open_output(
                            outputs.PyavOutput(out_path)
                        )

                        # Wait during recording.
                        await asyncio.sleep(float(pre_trigger_s + post_trigger_s))

                        self.trigger_video_output.close_output()

                        await asyncio.sleep(0)
                    except Exception as e:
                        self.logger.debug("Exception in _trigger_video_loop: " + str(e))

            finally:
                self.picam2.stop_encoder(self.trigger_video_encoder)
                await asyncio.sleep(0)
                message = self.camera_name + ": Trigger video: " + str(out_path)
                wirc_core.client_info.write_log("info", message)
                await asyncio.sleep(0)

        except Exception as e:
            self.logger.debug("Exception in _trigger_video_loop: " + str(e))

        finally:
            # Release.
            self.trigger_video_active = False
            self.logger.debug("_trigger_video_loop ended.")

    def trigger_video_trigger_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_video_trigger_event()
        self.video_trigger_event = asyncio.Event()
        old_event.set()

    def get_video_trigger_event(self):
        """ """
        if self.video_trigger_event == None:
            self.video_trigger_event = asyncio.Event()
        return self.video_trigger_event


class PreviewStreamingOutput(io.BufferedIOBase):
    """ """

    def __init__(self):
        """ """
        self.preview_queue = None

    def set_preview_queue(self, preview_queue):
        """ """
        self.preview_queue = preview_queue

    def write(self, buf):
        """ """
        try:
            if self.preview_queue != None:
                while self.preview_queue.qsize() > 2:
                    self.preview_queue.get_nowait()
                    self.preview_queue.task_done()
                if not self.preview_queue.full():
                    self.preview_queue.put_nowait(buf)
        except Exception as e:
            print("Exception: PreviewStreamingOutput write: ", e)
