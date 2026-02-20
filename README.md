# CloudedBats - WIRC-2026

Welcome to WIRC-2026, the Do-It-Yourself infrared/thermal camera system for bat monitoring.

## What is WIRC-2026?

WIRC stands for Wireless InfraRed Camera.

The software can handle both near-infrared (NIR) and far-infrared (FIR) cameras.

For near-infrared we use cameras without IR-cut filters
and we also need to use infrared light sources.
Far infrared is used to detect temperatures and we need to use special thermal cameras.

WIRC-2026 is an extension to WURB-2026 that is used to record ultrasonic sound.
Read more about WURB-2026 here: <https://github.com/cloudedbats/wurb_2026>

**Please note that WIRC-2026 is under development.**
The software is stable and reliable, but more configuration development needs to be done.

## Short introduction

It is not easy to monitor and study nocturnal, fast-flying mammals that we normally cannot hear
or cannot see in the middle of the night.
Therefore, we need tools to both hear and see them. 
There are not many camera systems that can handle fast-flying bats
and this software is an attempt to fix that problem.

Some notes on the subject:

- To capture fast moving objects, you need a camera sensor with a high readout speed, or even better, global shutter speed.

- IR filters must be removed, or even better, a monochrome sensor should be used.

- Then you need infrared light sources that produce light with a wavelength of around 850 nm.

- With more light, the exposure time for each frame in a video can be reduced,
and that is the key to better image quality for bats in flight.

The good news is that there are inexpensive monochrome global shutter sensors available for the
Raspberry Pi minicomputer.
USB thermal cameras are more expensive but in the same price range as a good ultrasonic microphone.

## Hardware

TODO

## Installation

Since this is an extension of the WURB-2026 system, you should install WURB-2026 first. 
This should be done even if you do not plan to record audio. 
Instructions can be found here: <https://github.com/cloudedbats/wurb_2026>

There is a small difference for installed python libraries when using the Raspberry Pi.
It is recommended to use "apt" to install the "picamera2" library and not to use "pip install"
for that part.
Therefore some libraries are installed outside the virtual environment
that is normally used for python libraries.

Note that both the WIRC and WURB systems should be installed with the "wurb" user.
This is because it should be possible to run them i parallel.

Install some extra Linux/Debian packages.

    sudo apt install python3-picamera2 -y
    sudo apt install python3-opencv -y
    sudo apt install ffmpeg -y
    sudo apt autoremove

Install the WIRC-2026 software.
(The "--system-site-packages" is used to allow access to software from outside the
virtual environment.)

    git clone https://github.com/cloudedbats/wirc_2026.git
    cd wirc_2026/
    python -m venv --system-site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt

Run it as a service.

    sudo cp /home/wurb/wirc_2026/raspberrypi_files/wirc_2026.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wirc_2026.service
    sudo systemctl start wirc_2026.service

## Attached cameras

Attached cameras should be available after a reboot if they are directly supported by Raspberry Pi.

If you use other cameras like the OV9281 you have to tell the system what you are using.
Raspberry Pi 5 supports two cameras (cam0 and cam1) and the other models supports one.

    sudo nano /boot/firmware/config.txt

    # Replace "camera-auto-detect=1" with
    camera-auto-detect=0
    
    # At the end of the file add this:
    dtoverlay=ov9281

    # If you are using Raspberry Pi 5 and want to connect two cameras you have to add
    # it like this (with two different global shutter cameras as an example):
    dtoverlay=ov9281,cam0
    dtoverlay=imx296,cam1

A reboot is needed after the update of the "/boot/firmware/config.txt" file.

    sudo reboot

## Web app and API

Then it should be possible to start the web application in a browser connected to the same local network.

    http://wurb01.local:8082

The API if you want to use it as a backend, can be found here:

    http://wurb01.local:8082/docs

## Configuration, logging and recorded files

There are three directories with important content when using WIRC.
The structure is the same as for WURB, but external USB devices can't be used yet
(but is on the TODO-list).

- **/home/wurb/wirc_settings** contains a yaml file with extra configuration parameters.
- **/home/wurb/wirc_logging** contains log files.
- **/home/wurb/wirc_recordings** contains the recorded videos and captured images.

## Remote access

The instructions above is about a Raspberry Pi connected to a local network.
Then it should be accesses with ".local", like in this example: **http://wurb01.local:8082**

If the Raspberry Pi is setup like a hotspot it should be accessed like this **http://10.42.0.1:8082**
A detailed instruction for this is available in the "CloudedBats WURB-2024" repository.

My personal favorite is to use **Tailscale**, https://tailscale.com/, where even remotely
deployed detectors can be accessed in the same way as if they where locally installed.
The address will then be **http://wurb01:8082** if it is accessed from a desktop computer or mobile phone where Tailscale is installed.
The requirement is then that the Raspberry Pi is connected to internet, and this can be done with
cable, wifi or by using a 4G/LTE modem.

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>
