dcraspaper
=============
## What to expect
A simple python script that provides a Decred information dashboard for the Raspberry Pi equipped with a Waveshare EPaper display.

Informations get requested trough the api's at [dcrdata.decred.org](https://dcrdata.decred.org) and [Politeia](https://proposals.decred.org).

A [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/) with a [Waveshare EPaper 2.13inch](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT) was used, but various other waveshare EPaper displays are supported. Take a look into the /lib directory and configure the script accordingly.
## Preparations
The following steps will help you setting up your own dcraspaper.
### Configuring your Pi
Please download the latest [Raspian lite](https://www.raspberrypi.org/downloads/raspbian/) and write the image onto a sd card. The next steps will enable you to access the device via ssh and preconfigure a wifi connection.
#### ssh access
Since the Raspian Buster release the ssh server is disabled by default. To enable the ssh server you have to generatie an empty file called `ssh` in the root folder of the `boot` partition. You will now be able to connect via ssh with the username `pi`and password `raspberry`.
#### wifi connection
You can have your Pi automatically connect to your wifi network by editing the `etc/wpa_supplicant/wpa_supplicant.conf` file with the following config example. Please replace your wifi credentials and encryption.
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
ssid="WIFI_SSID"
scan_ssid=1
psk="WIFI_PASSWORD"
key_mgmt=WPA-PSK
}
```
### enable GPIO pins
The Waveshare EPaper 2.13inch Hat display fits perfectly onto the GPIO pins of the Raspberry Pi. But in order to use the GPIO interface you have to enable it by editing the `/boot/config.txt` file and uncommend the following line.
```
dtparam=spi=on
```
The preperations of the sd card are now finished. Put the sd card into your Raspberry Pi and launch it. Connect to your Pi via ssh, the following steps will guide you trough the process of installing the needed software dependencies.
### installing the software
```
  $ sudo apt update
  $ sudo apt install python-pip
  $ sudo apt install python-pil
  $ sudo apt install python-numpy
  $ sudo apt install git
  $ sudo pip install RPi.GPIO
  $ sudo pip install spidev
  $ sudo pip install ascii_graph
```
It is suggested to change the default password of your ssh login with the following command:
```  $ passwd```
  
Clone this repository and execute the script. You can quit the execution at any time with the ctrl+c combination.
```
  $ git clone https://github.com/karamble/dcraspaper.git
  $ cd dcraspaper
  $ python dcraspaper.py
```  
  
## License

dcraspaper is released under a permissive ISC license.

For simplification the waveshare display libraries for python are copied to this repository. You can find the full package at [https://github.com/waveshare/e-Paper.git](https://github.com/waveshare/e-Paper.git).
