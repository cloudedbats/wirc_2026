# wirc_2026

WIRC-2025, the DIY infrared/thermal camera system for bat monitoring.


## Installation

This is a short instruction on how to install camera support on a Raspberry Pi computer.

The installation is similar to the one used for CloudedBats WURB-2024,
but there is a difference for installed python libraries.
It is recommended to use "apt" to install the "picamera2" library. 
Therefore some libraries are installed outside the virtual environment that is normally used for python libraries.

The first step is to use the **Raspberry Pi Imager** to install the **Raspberry Pi OS** on a SD card.

Note that both the WIRC and WURB systems should be installed with the "wurb" user.
This is because it should be possible to run them i parallell.

Use these settings, or similar, when running the **Raspberry Pi Imager**:

- Select OS version: **Raspberry Pi OS Lite (64-bit)**. 
- Hostname: wurb01
- User: wurb
- Password: your-secret-password
- WiFi SSID: your-home-network
- Password: your-home-network-password
- Wireless LAN country: your-country-code
- Time zone: your-time-zone
- Activate SSH.

Connect to the Raspberry Pi with SSH and do an update.

    ssh wurb@wurb01.local
    
    sudo apt update
    sudo apt upgrade -y

Install Linux packages.

    sudo apt install git python3-venv python3-dev -y
    sudo apt install libopenblas-dev pmount -y
    sudo apt install python3-picamera2 -y
    sudo apt install python3-opencv -y
    sudo apt install ffmpeg -y
    sudo apt autoremove

Install the software in this repository.

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

A reboot is needed after the update of the "config.txt" file.

    sudo reboot

## Web app and API

Then it should be possible to start the web application in a browser connected to the same local network.

    http://wurb01.local:8082

The API if you want to use it as a backend, can be found here:

    http://wurb01.local:8082/docs

## Configuration, logging and recorded files

There are three dirctories with important content when using WIRC.

- **/home/wurb/wirc_settings** contains a yaml file with extra configuration parameters.
- **/home/wurb/wirc_logging** contains log files.
- **/home/wurb/wirc_recordings** contains the recorded videos and captured images.

## Remote access

The instructions above is about a Raspberry Pi connected to a local network.
Then it should be accesses with ".local", like in this example: **http://wurb01.local:8082**

If the Raspberry Pi is setup like a hotspot it should be accessed like this **http://10.42.0.1:8080**
A detaild instruction for this is available in the "CloudedBats WURB-2024" repository.

My personal favorite is to use **Tailscale**, https://tailscale.com/, where even remotely deployed detectors 
can be accessed in the same way as if they where locally installed. 
The address will then be **http://wurb01:8082** if it is accessed from a desktop computer or mobile phone 
where Tailscale is installed.
The requirement is then that the Raspberry Pi is connected to internet, and this can be done with cable, wifi or 
by using a 4G/LTE modem.

## Feedback

This system was developed during a period when bats hibernate.
Therefore, I have not tested it on flying bats yet and there will probably be changes when
theory meets reality.
Please provide feedback if you try it yourself. Contact details below.

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>
