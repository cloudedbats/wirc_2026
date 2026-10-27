#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import pathlib
import logging
import cv2
import PIL
import io
from datetime import datetime, timedelta

import wirc_core


class ThermalCamera:
    """ """

    def __init__(
        self,
        config={},
        logger_name="DefaultLogger",
        config_id="usb-cam0",
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
        # Trigger.
        self.video_trigger_event = None
        self.video_trigger_timestamp = 0

    def clear(self):
        """ """
        self.camera_mode = "camera-off"
        self.preview_mode = "preview-off"
        self.camera_active = False
        self.preview_active = False
        self.camera_video_active = False
        self.camera_task = ""
        self.camera_info = ""
        self.trigger_video_active = False
        self.trigger_video_task = None
        self.save_to_circular_buffer = True
        self.camera_device_index = None

    def configure(self):
        """ """
        conf = self.config
        cam = self.config_id
        #
        self.rpi_camera_id = self.config_id
        self.camera_info = "Config id: " + self.config_id + "."
        self.startup_mode = conf.get(cam + ".settings.startup_mode", False)

        # self.camera_id = camera_id
        # self.hflip = hflip
        # self.vflip = vflip
        # self.video_framerate_fps = video_framerate_fps

        # Use upper half.

        self.directory_name = conf.get(cam + ".video.directory_name", "WircStation")
        self.date_option = conf.get(cam + ".video.date_option", "date-post-before")
        self.file_prefix = conf.get(cam + ".video.file_prefix", self.camera_name)

    def set_camera_device_index(self, device_index):
        """ """
        self.camera_device_index = device_index

    def get_camera_status(self):
        """ """
        camera_status = {}
        camera_status["camera_device_index"] = self.camera_device_index
        camera_status["camera_mode"] = self.camera_mode
        camera_status["preview_mode"] = self.preview_mode
        camera_status["exposure_time_us"] = "disabled"
        camera_status["camera_gain"] = "disabled"
        camera_status["video_framerate_fps"] = "disabled"
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

        message = self.camera_name + ": " + str(self.camera_mode) + "."
        wirc_core.client_info.write_log("info", message)

        if self.camera_mode == "camera-off":
            await self.stop_camera()
            await asyncio.sleep(0)
            return

        if self.preview_mode == "preview-off":
            await self.stop_preview()
            await asyncio.sleep(0)
        else:
            await self.start_camera()
            await asyncio.sleep(0)
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
            await self.start_camera()
            await asyncio.sleep(0)
            await self.start_video()
            await asyncio.sleep(0)

        if self.camera_mode == "record-on-trigger":
            await self.start_camera()
            await asyncio.sleep(0)
            await self.start_trigger_video()
            await asyncio.sleep(0)

    async def video_trigger(self):
        """ """
        self.video_trigger_timestamp = datetime.now()
        self.trigger_video_trigger_event()

    async def initiate_camera(self):
        """ """
        self.camera_initiated = True

    # async def config_camera_controls(self):
    #     """ """
    #     try:
    #         await self.set_camera_controls(
    #             self.exposure_time_us,
    #             self.camera_gain,
    #             self.saturation,
    #             self.video_framerate_fps,
    #         )

    #     #     # print(
    #     #     #     "DEBUG: self.picam2.controls.AeEnable: " + str(self.picam2.camera_controls["AeEnable"])
    #     #     # )
    #     #     self.picam2.set_controls({"AeEnable": False})
    #     #     # self.picam2.controls.AeEnable = False

    #         await asyncio.sleep(0)
    #     except Exception as e:
    #         self.logger.debug("Exception in config_camera_controls: " + str(e))

    async def set_camera_controls(
        self,
        exposure_time_us=None,
        camera_gain=None,
        saturation=None,
    ):
        """ """
        #
        # NOT USED...
        # Rotation ?
        #

    async def start_camera(self):
        """ """
        try:
            if self.camera_active == True:
                return

            self.camera_active = True
            self.camera_task = asyncio.create_task(
                self._thermal_camera_loop(), name="Thermal camera loop"
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_camera (thermal): " + str(e))

    async def stop_camera(self):
        """ """
        self.preview_mode = "preview-off"
        self.camera_initiated = False
        try:
            self.camera_active = False
            await asyncio.sleep(0)
            if self.camera_task:
                self.camera_task.cancel()
            await asyncio.sleep(0)
            self.camera_task = None
        except Exception as e:
            self.logger.debug("Exception in stop_camera (thermal): " + str(e))

    async def start_preview(self, preview_mode=None):
        """ """
        try:
            self.preview_active = True
            #
            self.preview_quality = "MEDIUM"
            self.preview_quality_persent = 75
            self.preview_fps = 10
            if preview_mode:
                if preview_mode == "preview-on":
                    self.preview_quality = "MEDIUM"
                    self.preview_quality_persent = 75
                    self.preview_fps = 10
                elif preview_mode == "fullsize-10fps":
                    self.preview_quality = "MEDIUM"
                    self.preview_quality_persent = 75
                    self.preview_fps = 10
                elif preview_mode == "preview-5fps":
                    self.preview_quality = "LOW"
                    self.preview_quality_persent = 40
                    self.preview_fps = 5
                elif preview_mode == "preview-2fps":
                    self.preview_quality = "LOW"
                    self.preview_quality_persent = 40
                    self.preview_fps = 2
                elif preview_mode == "preview-1fps":
                    self.preview_quality = "VERY_LOW"
                    self.preview_quality_persent = 10
                    self.preview_fps = 1
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_preview: " + str(e))

    async def stop_preview(self):
        """ """
        try:
            self.preview_active = False
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_preview: " + str(e))

    async def start_video(self):
        """ """
        try:
            self.camera_video_active = True
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        try:
            self.camera_video_active = False
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))

    async def _thermal_camera_loop(self):
        """ """
        try:
            self.camera_active = True

            # capture = cv2.VideoCapture(self.camera_device_index)
            capture = cv2.VideoCapture(
                self.camera_device_index, apiPreference=cv2.CAP_V4L2
            )

            if not capture.isOpened():
                message = "Error: Could not access the webcam."
                wirc_core.client_info.write_log("info", message)
                await asyncio.sleep(0.0)
                self.set_camera_mode(camera_mode="camera-off")
                wirc_core.client_status.trigger_status_event()
                await asyncio.sleep(0.0)
                return

            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            self.current_frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.current_frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            frame_rate_fps = int(capture.get(cv2.CAP_PROP_FPS))
            print("DEBUG: frame_rate_fps: ", frame_rate_fps)
            capture.set(cv2.CAP_PROP_FPS, 30)
            self.current_frame_rate_fps = int(capture.get(cv2.CAP_PROP_FPS))
            print("DEBUG: current_frame_rate_fps: ", self.current_frame_rate_fps)

            # Used by record.
            now = datetime.now()
            next_time = now + timedelta(seconds=60)
            self.next_time_minute = next_time.replace(
                second=0,
                microsecond=0,
                minute=next_time.minute,
                hour=next_time.hour,
            )
            self.record_video_writer = None
            self.trigger_video_writer = None

            # Used by triggered record.
            self.circular_buffer_size_s = 2.0
            self.circular_buffer_size = (
                self.circular_buffer_size_s * self.current_frame_rate_fps
            )
            self.circular_frame_list = []
            self.triggered_video_writer = None

            # Used by preview.
            self.preview_time_counter = 0.0

            while self.camera_active:

                rc, image_array = capture.read()
                if not rc:
                    await asyncio.sleep(0.04)
                    continue

                # For recording.
                if self.camera_video_active or self.record_video_writer:
                    self.videoframes_for_record(image_array)

                # For triggered recording.
                # if self.trigger_video_active or self.triggered_video_writer:
                if self.trigger_video_active:
                    self.videoframes_for_triggered_record(image_array)

                # if self.camera_video_active:
                #     # Use one minute.
                #     if datetime.now() >= next_time_minute:
                #         # Save to file.
                #         if video_writer != None:
                #             video_writer.write_to_file()
                #             video_writer = None
                #             self.logger.debug(
                #                 "Thermal video saved. Time: " + str(datetime.now())
                #             )
                # else:
                #     # Save when video is not active.
                #     if video_writer != None:
                #         video_writer.write_to_file()
                #         video_writer = None
                #         self.logger.debug(
                #             "Thermal video saved. Time: " + str(datetime.now())
                #         )

                # if self.camera_video_active:
                #     if video_writer == None:
                #         now = datetime.now()
                #         next_time = now + timedelta(seconds=60)
                #         next_time_minute = next_time.replace(
                #             second=0,
                #             microsecond=0,
                #             minute=next_time.minute,
                #             hour=next_time.hour,
                #         )

                #         date_and_time = now.strftime("%Y%m%dT%H%M%S")
                #         file_mp4_name = self.file_prefix + "_" + date_and_time + ".mp4"
                #         video_writer = VideoFileWriter(
                #             camera_name=self.camera_name,
                #             file_mp4_name=file_mp4_name,
                #             frame_height=frame_height,
                #             frame_width=frame_width,
                #             fps=self.current_frame_rate_fps,
                #             directory_name=self.directory_name,
                #             date_option=self.date_option,
                #         )
                #         self.logger.debug(
                #             "Thermal video started. Time: " + str(datetime.now())
                #         )

                # # For saved video.
                # try:
                #     if self.camera_video_active:
                #         # Write the frame to the output video file
                #         video_writer.add_frame(image_array)
                # except Exception as e:
                #     self.logger.debug("Exception VIDEO: " + str(e))

                # For preview streaming.
                if self.preview_active == True:
                    self.videoframes_for_preview(image_array)

                await asyncio.sleep(0)

            # While loop ended.
            if self.record_video_writer != None:
                self.record_video_writer.write_to_file()
                self.record_video_writer = None

            # While loop ended.
            if self.triggered_video_writer != None:
                self.triggered_video_writer.write_to_file()
                self.triggered_video_writer = None

        except Exception as e:
            self.logger.debug("Exception in _thermal_camera_loop: " + str(e))

        finally:
            # Release.
            self.camera_active = False
            capture.release()
            self.logger.debug("Thermal_camera_loop ended.")

    def videoframes_for_record(self, image_array):
        """ """
        try:
            if self.camera_video_active:
                # Use one minute.
                if datetime.now() >= self.next_time_minute:
                    # Save to file.
                    if self.record_video_writer != None:
                        self.record_video_writer.write_to_file()
                        self.record_video_writer = None
                        self.logger.debug(
                            "Thermal video saved. Time: " + str(datetime.now())
                        )
            else:
                # Save when video is not active.
                if self.record_video_writer != None:
                    self.record_video_writer.write_to_file()
                    self.record_video_writer = None
                    self.logger.debug(
                        "Thermal video saved. Time: " + str(datetime.now())
                    )

            if self.camera_video_active:
                if self.record_video_writer == None:
                    now = datetime.now()
                    next_time = now + timedelta(seconds=60)
                    self.next_time_minute = next_time.replace(
                        second=0,
                        microsecond=0,
                        minute=next_time.minute,
                        hour=next_time.hour,
                    )

                    date_and_time = now.strftime("%Y%m%dT%H%M%S")
                    file_mp4_name = self.file_prefix + "_" + date_and_time + ".mp4"
                    self.record_video_writer = VideoFileWriter(
                        camera_name=self.camera_name,
                        file_mp4_name=file_mp4_name,
                        frame_height=self.current_frame_height,
                        frame_width=self.current_frame_width,
                        fps=self.current_frame_rate_fps,
                        directory_name=self.directory_name,
                        date_option=self.date_option,
                    )
                    self.logger.debug(
                        "Thermal video started. Time: " + str(datetime.now())
                    )

            # For saved video.
            try:
                if self.camera_video_active:
                    # Write the frame to the output video file
                    self.record_video_writer.add_frame(image_array)

            except Exception as e:
                self.logger.debug("Exception VIDEO: " + str(e))
        except Exception as e:
            self.logger.debug("Exception in videoframes_for_record: " + str(e))

    def videoframes_for_triggered_record(self, image_array):
        """ """
        try:
            if self.save_to_circular_buffer == True:
                self.circular_frame_list.append(image_array)
                while len(self.circular_frame_list) > self.circular_buffer_size:
                    self.circular_frame_list.pop(0)
            else:
                if self.trigger_video_writer != None:
                    self.trigger_video_writer.add_frame(image_array)

        except Exception as e:
            self.logger.debug(
                "Exception in videoframes_for_triggered_record: " + str(e)
            )

    def videoframes_for_preview(self, image_array):
        """ """
        try:
            self.preview_time_counter += 1 / self.current_frame_rate_fps
            if self.preview_time_counter >= 1 / self.preview_fps:
                self.preview_time_counter = 0
                #
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                jpg = PIL.Image.fromarray(image_rgb)
                tmpFile = io.BytesIO()
                jpg.save(tmpFile, "JPEG", quality=self.preview_quality_persent)
                bytearray = tmpFile.getvalue()[:]  # Copy. Needed?
                try:
                    while self.preview_queue.qsize() > 2:
                        self.preview_queue.get_nowait()
                        self.preview_queue.task_done()
                    if not self.preview_queue.full():
                        self.preview_queue.put_nowait(bytearray)
                except Exception as e:
                    self.logger.debug("Exception in _thermal_camera_loop: " + str(e))
        except Exception as e:
            self.logger.debug("Exception in videoframes_for_preview: " + str(e))

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
            self.logger.debug("Exception in start_trigger_video: " + str(e))

    async def stop_trigger_video(self):
        """ """
        try:
            if self.trigger_video_active == True:
                self.trigger_video_task.cancel()
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_trigger_video: " + str(e))

    async def _trigger_video_loop(self):
        """ """
        self.trigger_video_active = True
        out_path = ""
        trigger_startup_time_s = 0.5
        trigger_before_s = 2.0
        trigger_after_s = 6.0
        trigger_max_video_length_s = 60.0

        try:
            try:
                # Get trigger event.
                video_trigger_event = self.get_video_trigger_event()
                await asyncio.sleep(0)

                while True:
                    self.save_to_circular_buffer = True
                    # Wait until trigger event is set.
                    await video_trigger_event.wait()
                    # Used for next trigger events.
                    video_trigger_event = self.get_video_trigger_event()

                    # Check if the last event already is covered by video.
                    last_video_end_time = self.video_trigger_timestamp + timedelta(
                        milliseconds=int(trigger_after_s * 1000.0)
                    )
                    if last_video_end_time < datetime.now():
                        continue  # Skip video.

                    now = datetime.now() - timedelta(
                        milliseconds=int(
                            (trigger_startup_time_s + trigger_before_s) * 1000.0
                        )
                    )
                    date_and_time = now.strftime("%Y%m%dT%H%M%S")
                    file_mp4_name = self.file_prefix + "_" + date_and_time + ".mp4"

                    disc_path = wirc_core.wirc_files.get_target_disc_path()
                    dir_path = wirc_core.wirc_files.get_target_dir_path(
                        disc_path,
                        directory_name=self.directory_name,
                        date_option=self.date_option,
                    )
                    trigger_video_mp4_path = pathlib.Path(dir_path, file_mp4_name)

                    try:
                        out_path = str(trigger_video_mp4_path).replace(
                            ".mp4", "_" + "_TRIGGER.mp4"
                        )

                        message = self.camera_name + ": Trigger video: " + str(out_path)
                        wirc_core.client_info.write_log("info", message)

                        # Create file_writer object.
                        self.trigger_video_writer = VideoFileWriter(
                            camera_name=self.camera_name,
                            file_mp4_name=out_path,
                            frame_height=self.current_frame_height,
                            frame_width=self.current_frame_width,
                            fps=self.current_frame_rate_fps,
                            directory_name=self.directory_name,
                            date_option=self.date_option,
                        )
                        self.logger.debug(
                            "Thermal video started. Time: " + str(datetime.now())
                        )

                        # Write stored frames from circular list.
                        circular_copy = self.circular_frame_list.copy()
                        self.save_to_circular_buffer = False
                        self.circular_frame_list = []
                        for stored_frame in circular_copy:
                            self.trigger_video_writer.add_frame(stored_frame)

                        start_rec_time = datetime.now()
                        await asyncio.sleep(float(trigger_before_s))
                        # Wait until trigger_after or max_video_length.
                        recorded_time = (
                            datetime.now() - start_rec_time
                        ).total_seconds()
                        while recorded_time < trigger_max_video_length_s:
                            time_now = datetime.now()
                            # Using video_trigger_timestamp to catch more events.
                            if time_now < (
                                self.video_trigger_timestamp
                                + timedelta(milliseconds=int(trigger_after_s * 1000.0))
                            ):
                                await asyncio.sleep(1.0)
                                recorded_time = (
                                    datetime.now() - start_rec_time
                                ).total_seconds()
                            else:
                                break
                        # Done.
                        self.trigger_video_writer.write_to_file()

                        message = (
                            self.camera_name
                            + ": Triggered video ended after "
                            + str(round(recorded_time, 1))
                            + " sec."
                        )
                        wirc_core.client_info.write_log("info", message)

                        await asyncio.sleep(0)
                    except Exception as e:
                        self.logger.debug("Exception in _trigger_video_loop: " + str(e))

            finally:
                self.picam2.stop_encoder(self.trigger_video_encoder)
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


class VideoFileWriter(object):
    """ """

    def __init__(
        self,
        camera_name,
        file_mp4_name,
        frame_height,
        frame_width,
        fps,
        directory_name,
        date_option,
    ):
        """ """
        self.camera_name = camera_name
        self.file_mp4_name = file_mp4_name
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.fps = fps
        self.directory_name = directory_name
        self.date_option = date_option
        #
        self.frames = []
        self.write_task = None

    def add_frame(self, frame):
        """ """
        self.frames.append(frame)

    def write_to_file(self):
        """ """
        disc_path = wirc_core.wirc_files.get_target_disc_path()
        dir_path = wirc_core.wirc_files.get_target_dir_path(
            disc_path,
            directory_name=self.directory_name,
            date_option=self.date_option,
        )
        self.out_path = pathlib.Path(dir_path, self.file_mp4_name)

        if not self.out_path.parent.exists():
            self.out_path.parent.mkdir(parents=True)
        self.write_task = asyncio.create_task(
            self._write_to_file_task(), name="Write to file task"
        )
        #
        message = self.camera_name + ": Video stored: " + str(self.out_path)
        wirc_core.client_info.write_log("info", message)

    def cancel(self):
        """ """
        if self.write_task:
            self.write_task.cancel()

    async def _write_to_file_task(self):
        """ """
        out = None
        try:
            fourcc = cv2.VideoWriter_fourcc(*"avc1")  # AVC1 is equal to H.264.
            out = cv2.VideoWriter(
                self.out_path, fourcc, self.fps, (self.frame_width, self.frame_height)
            )
            for frame in self.frames:
                out.write(frame)
                await asyncio.sleep(0)
        finally:
            if out:
                out.release()
            await asyncio.sleep(0)
