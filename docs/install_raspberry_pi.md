# Installing on a Raspberry Pi

I have had great success in following the Linux install instructions for a standard Raspberry Pi.

This is a very cheap (~£30) mini computer which runs Linux.  With a serial port adapter and a USB
power supply it becomes your very own terminal adapter for the V-Mixer.  With Raspberry Pi 3 you
can easily set it up to connect via WiFi to a router.

The original Raspberry Pi 1 is more than powerful enough.  VMXProxy runs happily on this, however
you will need to make sure there is still support of the Raspbian image (which at Jan 2019 - is
still supported).

There should be no issue running on a Raspberry Pi 2 or 3 (ARMv7).

See <http://www.raspberrypi.org/> for more info.  Ethernet is just plug and play (if you're happy
with DHCP), but otherwise setting up networking is beyond the scope of this readme (but there is
plenty of guidance on the web for you).


## Overview

I've provided a lot of detail down here, but it shouldn't be too complicated, nor take too long.

If you follow the instructions, and you have a computer on the same network, you shouldn't need a
keyboard, monitor or mouse for the Raspberry Pi.

Steps:

- Download RASPBIAN STRETCH LITE image (~300 Mbytes)
- Install on SD Card (8GB+) using Etcher (windows tool)
- Setup ssh to work on first boot
- (optional) setup WiFi details
- Power up and Boot the Pi
- Install a (free) network scanner to find your Pi (the IP address)
- Log on using ssh via a (free) application called Putty
- Execute a few commands to install dependencies
- Alter a few files with your settings (e.g. passcodes.txt)
- Execute a few more commands to make it automatically run

All these steps can be done to setup a Simulator so you can get this working without the Mixer and
then it is a couple of quick command to switch over to a real (Mixer) setup.


## Downloading the Raspbian image

I've used RASPBIAN STRETCH LITE successfully <https://www.raspberrypi.org/downloads/raspbian/>
(non desktop and the smallest download), but any version of raspbian should be okay.

- <https://www.raspberrypi.org/downloads/raspbian/>

I use Etcher to create SD image - <https://etcher.io/>

- Used 8GB SD Card (but only 2G is needed)


## Enable SSH

Before you boot for the first time, add the following file to the SD Card

- `ssh`  (no extension, empty file)

This will enable SSH on first boot.


## Enabling Wifi

This can be done in advance of first boot by placing another file on the created SD Card.  If you
want to use WiFi and you're using STETCH LITE you'll probably want to do this step as you don't
have a nice GUI to set this up later.

- `wpa_supplicant.conf`  (with you wifi credentials and config)

See https://www.e-tinkers.com/2017/03/boot-raspberry-pi-with-wifi-on-first-boot/


## First boot

Once that is in place, boot it, and you can just follow the instructions for Linux above to
install and get a service running (you won't need to install git or python as they will already
be installed).

The Raspberry Pi boots within 20 seconds, and needs no user interaction, so can be boxed and left
to be powered up and down with the mixer.


## Install a network scanner on your phone.

Once booted you'll need to know the Raspberry Pi's IP address.  There are helpful (free) Android
apps that can search the network for you.

- [Network Analyzer](https://play.google.com/store/apps/details?id=net.techet.netanalyzerlite.an)
- [Fing](https://play.google.com/store/apps/details?id=com.overlook.android.fing)

I recommend Network Analyzer (Net Analyzer).

To Scan your network:

- Click triple bar menu top left
- select `LAN Scan`
- select `Scan`
- wait for ~30 seconds
- look down the list until you find "Raspberry Pi Foundation" (raspberrypi).  There is its
  IP address.


## Install VMXProxy

Download [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html), an SSH client
that will let you execute commands on the Raspberry Pi.

- Start Putty
- Make sure the connection type is SSH (Port 22)
- In the "Host Name" enter the IP address you found above
- Click Open

Enter in the username `pi`, and the password `raspbian`.

First thing you should do is *Change the password!*  Do this by typing:

    passwd

(entering in the old password `raspbian` and then your new password)

The Raspberry Pi is a Linux device, so now follow the instructions for
[installing on Linux](install_linux.md).


### Upgrading

The Android App manages most of the complex functionality, and so VMXProxy is fairly stable.  There
has been no need to upgrade in last 4 years.  In 2018 Python 3 support was added, and GUI to aid
configuration for windows users, but otherwise changes are to the documentation and install scripts
keeping them up-to-date.

That said, updating is described in [Linux](install_linux.md).

Just use Putty again to connect using SSH (and you're new password).  This can be done in situ, as
you don't need a screen to do it, and you could even get an SSH client (to replace putty) for your
phone.

- [JuiceSSH](https://play.google.com/store/apps/details?id=com.sonelli.juicessh)


---
JamesCC @ 01feb2019