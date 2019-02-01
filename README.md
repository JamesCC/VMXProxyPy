# VMXProxy

github: <https://github.com/JamesCC/VMXProxyPy>

website: <https://sites.google.com/site/vmxserialremote/>


## Introduction

A network to serial terminal server optimised for connection to Roland V-Mixer mixing consoles.
Intended to be used with VMX Serial Remote Android App.

It is python script, runs under Linux, Windows and (potentially) OSX.  There is a graphical
user interface to aid setting up.

There are three modes of operation...

  1. Network Simulation Mode - where VMXProxy pretends to be connected to a V-Mixer mixing
     console, but does not use a serial port.  Useful for testing the Android application.

  2. Proxy Mode - where VMXProxy does its primary purpose which is to forward on network
     traffic to the serial port (connected to a V-Mixer console) and echos the responses back.

  3. Serial Port Simulation Mode - where VMXProxy pretends to be a V-Mixer console.
     (only useful for testing VMXProxy itself, or Bluetooth adaptor setups)

V-Mixer mixing consoles have strict handshake protocol which is fine over a serial connection,
but over network traffic the long round trip delays can make the protocol very slow.

VMXProxy dramatically improves performance for the android app, as we are able to concatenate
query commands and their responses minimising that round trip delay.  It also can handle
multiple clients (apps) connecting to the mixer, and provides some caching to limit the
traffic going to the mixer's serial port.


## Installation

If you want to get going quickly, head straight to the installation guide for your chosen
platform.  This is to install and setup VMXProxy on the computer / device that will connect
your network to the mixer (serial port).

- Install VMXProxy on [Windows](docs/install_windows.md)
- Install VMXProxy on [Linux PC](docs/install_linux.md)
- Install VMXProxy on [Raspberry Pi](docs/install_raspberry_pi.md)


## Overview of Operation (Background)

A Roland V-Mixer Mixer Console accepts commands to allow adjustment of a variety of controls,
over the serial port.

These commands take the form of... `$CMD:I1,p1,p2;`

    Where $ is the ASCII character code 0x02 (STX),
    CMD is a three letter command code,
    I1 represents the input,
    p1, p2 are two parameters (exact number depends on the cmd),
    and all commands are terminated by a semicolon.

If accepted, the response is either of the same form... `$RSP:I1,p1,p2;`

    Where $ is the ASCII character code 0x02
    RSP is a three letter response code
    I1 represents the input described
    p1, p2 are two parameters (exact number depends on the response)
    All responses are terminated by a semicolon.

Or an ACK character code 0x06 (if no response information is needed).


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

The script is compatible with both Python 2.7 and Python 3.6+.

The -g option will present a GUI for providing the configuration or altering options already
provided on the command line.

The -z (--delay) and -x (--discard) options are only for stress testing the app, they will make
performance worse - *please don't use them*.

Windows users can use a compiled version of the script, to avoid needing to install python.  By
default it starts the GUI unless you give it options.


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


---
JamesCC @ 01feb2019
