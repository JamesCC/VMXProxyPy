# VMXProxy

<https://github.com/JamesCC/VMXProxyPy>
<https://sites.google.com/site/vmxserialremote/>


## Introduction

A network to serial terminal server optimised for connection to Roland V-Mixer mixing consoles.
Intended to be used with VMX Serial Remote Android App.

It is python script, runs under Linux, Windows and (potentially) OSX.  There is a graphical
user interface to aid setting up.

There are three modes of operation...

  1. Network Simulation Mode - where VMXProxy pretends to be connected to a V-Mixer mixing
     console, but does not use a serial port.  Useful for testing the Android application.

  2. Serial Port Simulation Mode - where VMXProxy pretends to be a V-Mixer console.

  3. Proxy Mode - where VMXProxy does its primary purpose which is to forward on network
     traffic to the serial port (connected to a V-Mixer console) and echo the responses back.

VMixer mixing consoles have strict handshake protocol which is fine over a serial connection,
but over network traffic the long round trip delays can make the protocol very slow.

VMXProxy dramatically improves performance for the android app, as we are able to concatenate
query commands and their responses minimising that round trip delay.  It also can handle
multiple clients (apps) connecting to the mixer, and provides some caching to limit the
traffic going to the mixer serial port.



## Overview of Operation

V-Mixer commands allow adjustment of a variety of controls, over the serial port.

These commands take the form... `$CMD:I1,p1,p2;`

    Where $ is the ASCII character code 0x02 (STX),
    CMD is a three letter command code,
    I1 represents the input,
    p1, p2 are two parameters (exact number depends on the cmd),
    and all commands are terminated by a semicolon.

If accepted, the response is either of the same form... `$RSP:I1,p1,p2;` or
an ACK character code 0x06 (if no response information is needed).

    Where $ is the ASCII character code 0x02
    RSP is a three letter response code
    I1 represents the input described
    p1, p2 are two parameters (exact number depends on the response)
    All responses are terminated by a semicolon.

VMXProxy forwards on these commands from a network socket to the serial port, and returns back the
responses.  It also allows concatenated commands by use of an & ampersand in place of the semicolon.
When it sees an ampersand it breaks up the command into a series of serial port commands,
concatenating the results before sending the results back en-mass.  This improves performance
significantly, important when we are already using a slow interface such as a serial port.

In simulation mode, VMXProxy will fake the responses from the mixer, but to the app it looks the
same.

A list of the commands is available on the Roland website, but VMXProxy only supports a subset of
them in simulation mode.  For more info see https://sites.google.com/site/vmxserialremote/the-concept
and the copy of Roland's VMixer RS232 protocol PDF in the docs directory of this repository.


## The Python Script

The heart of VMXProxy is a python script.  It accepts command line parameters.


    $ python -m VMXProxy -h
    usage: VMXProxy [-h] [-q] [-v] [-s PORT] [-b BAUD] [-n PORT] [-p FILE] [-z MS]
                    [-x X] [--version] [-g]

    Roland VMixer interface adaptor.  It can run in three modes.
    
     1. Simulation of VMX Proxy over a network        (if --serial without --net)
     2. Simulation of a VMixer itself over serial     (if --net without --serial)
     3. VMX Proxy - provide a bridge, specifically to handle the Roland VMixer
          protocol from network to a serial port      (if both --serial and --net)

    optional arguments:
      -h, --help            show this help message and exit
      -q, --quiet           quiet mode
      -v, --verbose         show debug
      -s PORT, --serial PORT
                            use serial port as proxy
      -b BAUD, --baud BAUD  serial port baud rate
      -n PORT, --net PORT   set host_port_number for network
      -p FILE, --passcodefile FILE
                            use passcode authentication
      -z MS, --delay MS     (debug) set random delay
      -x X, --discard X     (debug) set discard rate
      --version             show version
      -g, --gui             show GUI for altering configuration

The script is compatible with both Python 2.7 and Python 3.6.

The -g option will present a GUI for providing the configuration or altering options already
provided on the command line.

Windows users can use a compiled version of the script, to avoid needing to install python.  By
default it starts the GUI.


## Initialisation Files

There are two initialisation files read by VMXProxy on startup - passcodes.txt, and simrc.txt.
The location of these files are important, so don't move them.

These files are stored in the root of the project.  For windows this is C:/Program Files/VMXProxy
and users may need admin privaledges to alter these files.


### Access Control - passcodes.txt

When you start the server with the --passcodefile option (using start_proxy_secure.bat) you can
impose access restrictions to the server and what facilities can be controlled on the mixer by
the App. The file passcodes.txt is an example which is used by start_proxy_secure.bat.

The syntax is explained in the file, but in summary access control means:

    - Access is only allowed using one of the listed passcodes (number codes of any length)
    - Against each passcode are the permissions that passcode allows
        - Full Access - UNRESTRICTED
        - Allow or Disallow access to the Input Adjustment Screen - INPUTADJ
        - Allow or Disallow access to Main Faders - MAIN
        - Allow or Disallow access to specific AUX channels (or them all) - AUX

The main purpose of this is to prevent accidental adjustment of the wrong feeds by the wrong
people. For example you don't want your musicians accidentally altering the Main Faders.


### Simulator Setup - simrc.txt

Only interesting if you are testing the app.  This file is used for setting up the simulator, and
can be fun to play with to set-up the simulator with sensible names and levels for the various
channels.  You don't need to adjust this file, there are already some default values in it.

The simulator will validate the responses, so the commands on the left must correspond to the
expected responses on the right.  If you get it wrong, nothing disastrous will happen - when the
server is started (start_sim.bat) it will issue warnings, and the android app may struggle to
remain connected (since it might not get a needed input setting).

I recommend keeping a copy of the original simrc.txt.


## Prebuilt Executable for Windows

For windows you don't need to install Python, you can use a prebuilt executable, distributed as a
MSI file (windows installer).  Just double click to install, and an icon will be placed on your
desktop.

The installer can be found on the website, with details of how to run it...
<https://sites.google.com/site/vmxserialremote/vmxproxy>

In the installation there are additional batch files that can be used to start the server without
the use of the GUI.  Just double click the relevant batch file.  Edit them if necessary to change
any key settings (such as the serial port), and drop a short cut to them on your desktop to 
quickly execute them.


Alternatively, you can also run the python script "normally", just install Python 3.6, download
VMXProxy from github, start a windows console, cd to the directory you create (with this readme.md
file) and type...

    python -m VMXProxy --help

Note VMXProxy has a dependency on pyserial - https://pypi.python.org/pypi/pyserial


### Automatic Discovery

If you use the "Search for Server" option in the VMX Serial Remote App, you will need to install
Apple's Bonjour (if running in Windows).  Linux systems use the equivalent called avahi.  This
allows VMXProxy to advertise its ip address and port number.

Bonjour is used in a wide variety of places, not just Apple products.  If you don't have it
installed (check Control Panel / Program and Features), the simplest method is to get it is to
install iTunes.

I full understand if you might not want to do that.  You can install just Bonjour by itself by
downloading the itunes installer from http://www.apple.com/uk/itunes/ and using winrar or 7zip
to unpack the executable (yes you can do that).  Look for... .rsrc/RCDATA/CABINET and repeat
the unpack operation.  In there  you'll find Bonjour.msi.  Double click to install this
independently.


## Installing under Linux

### Basic environment

You will need root privileges.  For Fedora replace `apt-get` with `yum`

    sudo apt-get update
    sudo apt-get install git
    sudo apt-get install python3
    sudo apt-get install python3-pip

    python --version            # reported Python 2.7.13
    python3 --version           # reported Python 3.5.3
    
python is very likely to already be installed on your system.  It is recommended to use python3
where possible, although the script will work with python 2.7.

(Optional) If you wish to use avahi (bonjour) for advertising the server so that you can do 
automatic discovery of the ip address and port for VMXProxy...

    sudo apt-get install avahi-daemon avahi-utils
    sudo update-rc.d avahi-daemon defaults      # silent
    sudo /etc/init.d/avahi-daemon restart       # [ok]


Now you have the environment setup, get the VMXProxy code itself...

    cd $HOME
    git clone https://github.com/JamesCC/VMXProxyPy

VMXProxy has a python module dependency on pyserial.  In most cases this will have already been
installed as part of python, but you can check (and install) by...

    pip3 install pyserial

You can now run the script using...

    cd vmxproxypy
    python3 -m VMXProxy --help

You must run the script from this directory (where this readme file is), as VMXProxy expects to
find simrc.txt in the current directory.


### Installing as a Linux service (to start at bootup)

A sysV init script is used to create a service that will automatically run when the system boots.

To install the service use `make install` with OPTIONS set to the required arguments for when
starting VMXProxy.  For example, choose one of the following...

    sudo make install OPTIONS="--serial /dev/ttyUSB0 --net 10000"
    sudo make install OPTIONS="--serial /dev/ttyUSB0 --net 10000 --passcodefile=passcodes.txt"
    sudo make install OPTIONS="--net 10000 --passcodefile=passcodes.txt"

The first starts VMXProxy without passcode access control, the second with passcode control, the
third simulating the mixer (with passcode access control).

To remind yourself of the options type...

    python3 -m VMXProxy --help

Once you have run the above install command, to save you rebooting, start the service manually to
see if all is well...

    sudo /etc/init.d/VMXProxyStartup start      # start service

You can query the state of the service...

    sudo make install_status

Lastly, you can remove (uninstall) the service just by...

    sudo make uninstall


### Installing on a Raspberry Pi

I have had great success in following the above instructions for a standard Raspberry Pi Linux
install.  The original Raspberry Pi is more than powerful enough.

This is a very cheap (~£30) mini computer which runs Linux.  With a serial port adapter and a USB
power supply it becomes your very own terminal adapter for the V-Mixer.  Unless you buy a WiFi
dongle, you will need to connect it to your wireless router via an Ethernet cable.

See <http://www.raspberrypi.org/> for more info.

I used the Raspbian "Wheezy" Linux install.  Once that is in place you can just follow the
instructions for Linux above to install and get a service running (you won't need to install
git or python as they will already be installed).

The Raspberry Pi boots within 20 seconds, and needs no user interaction, so can be boxed and left
to be powered up and down with the mixer.


### Upgrading

If you are running windows, just download a new copy from the website, unzip it and copy in your
passcodes.txt and simrc.txt files from your old installation before you delete it.  You may have
also altered some .bat files for starting vmxproxy.

If you are running Linux, the following will upgrade your installation in place...

    cd $HOME/vmxproxypy
    git status

git status will report any changes you have made to the installation.  This is likely to be
only passcodes.txt, and maybe simrc.txt.  Copy those files so you can restore the file(s)
after the upgrade.

The following will revert any changes in the vmxproxypy directory (and any subdirectories),
and pull in the latest vmxproxy...

    git reset --hard
    git pull

Then copy back any files that have changed.  It is wise to check what you are overwriting
looks similar (in case the format of the files has changed during the upgrade).


---
JamesCC @ 10feb2018
