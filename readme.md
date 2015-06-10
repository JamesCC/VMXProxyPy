# VMXProxy

<https://bitbucket.org/JamesCC/vmxproxypy>
<https://sites.google.com/site/vmxserialremote/>


## Introduction

A network to serial terminal server optimised for connection to Roland V-Mixer mixing consoles.  
Intended to be used with VMX Serial Remote Android App.

It is python script, runs under Linux, Windows and (potentially) OSX.

There are three modes of operation...

  1. Network Simulation Mode - where VMXProxy pretends to be connected to a V-Mixer mixing 
     console, but does not use a serial port.  Useful for debugging the Android application.

  2. Serial Port Simulation Mode - where VMXProxy pretends to be a V-Mixer console

  3. Proxy Mode - where VMXProxy does its primary purpose which is to forward on network 
     traffic to the serial port (connected to a V-Mixer console) and echo the responses back.

VMixer mixing consoles have strict handshake protocol which is fine over a serial connection, 
but over network traffic the long round trip delays can make the protocol very slow.

VMXProxy dramatically improves performance for the android app, as we are able to concatenate
query commands and their responses minimising that round trip delay.



## Overview of Operation

V-Mixer commands allow adjustment of a variety of controls, over the serial port.

These commands take the form... `$CMD:I1,p1,p2;`

    Where $ is the character code 0x02 (STX), 
    CMD is a three letter command code,
    I1 represents the input,
    p1, p2 are two parameters (exact number depends on the cmd),
    and all commands are terminated by a semicolon.

If accepted, the response is either of the same form... `$RSP:I1,p1,p2;' or
an ACK character code 0x06 (if no response information is needed).

    Where $ is the character code 0x02, and RSP is a three letter response code
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
them.  See https://sites.google.com/site/vmxserialremote/ for those.



## The Python Script

The heart of VMXProxy is a python script.  It accepts command line parameters.

    $ python vmxproxypy -h
    Usage: vmxproxypy [options]

    Roland VMixer interface adaptor.  It can run in three modes.

     1. Provide a network serial interface, specifically to handle the Roland
        VMixer protocol  (--serial and --net options supplied)
     2. Provide an emulation of a VMixer over the network  (if no --serial option)
     3. Provide an emulation of a VMixer over serial  (if no --net option)

    Options:
      -h, --help            show this help message and exit
      -q, --quiet           quiet mode
      -v, --verbose         show debug
      -s PORT, --serial=PORT
                            use serial port as proxy
      -b BAUD, --baud=BAUD  serial port baud rate
      -n PORT, --net=PORT   set host_port_number for network
      -p FILE, --passcodefile=FILE
                            use passcode authentication
      -z MS, --delay=MS     (debug) set random delay
      -x X, --discard=X     (debug) set discard rate
      --version             show version

Windows users can use a compiled version of the script, to avoid needing to install python.



## Initialisation Files

There are two initialisation files read by VMXProxy on startup - passcodes.txt, and simrc.txt.
The location of these files are important, so don't move them.


### Access Control - passcodes.txt

When you start the server with the --passcodefile option (using start_proxy_secure.bat) you can 
impose access restrictions to the server and what facilities can be controlled on the mixer by 
the App. The file passcodes.txt is an example which is used by start_proxy_secure.bat.

The syntax is explained in the file, but in summary access control means:

    - Access is only allowed using one of the listed passcode (number codes of any length)
    - Against each passcode are the permissions that passcode allows
        - Full Access - UNRESTRICTED
        - Allow or Disallow access to the Input Adjustment Screen - INPUTADJ
        - Allow or Disallow access to Main Faders - MAIN
        - Allow or Disallow access to specific AUX channels (or them all) - AUX

The main purpose of this is to prevent accidental adjustment of the wrong feeds by the wrong 
people. For example you don't want your musicians accidentally altering the Main Faders.


### Simulator Setup - simrc.txt

Purely optional.  This file is used for setting up the simulator, and can be fun to play with to 
set-up the simulator with sensible names and levels for the various channels.  You don't need to 
adjust this file, there are already some default values in it.

The simulator will validate the responses, so the commands on the left must correspond to the 
expected responses on the right.  If you get it wrong, nothing disastrous will happen - when the 
server is started (start_sim.bat) it will issue warnings, and the android app may struggle to 
remain connected (since it might not get a needed input setting).

I recommend keeping a copy of the original simrc.txt. 


### Prebuilt Executable for Windows

For windows you don't need to install Python, you can use a prebuilt executable, distributed as a 
zip file.  Just unzip to a directory in a suitable place.  Uninstalling just involved deleting
the directory.

The zip fle can be found on the website, with details of how to install...  
<https://sites.google.com/site/vmxserialremote/vmxproxy>

Alternatively, you can also run the python script "normally", just install Python 2.7, unzip the
zip archive, start a windos console, cd to the directory you create (with this readme.md file) and
type...

    python VMXProxy --help


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

You will need root privaledges.  For Fedora replace `apt-get` with `yum`

    sudo apt-get update
    sudo apt-get install git
    sudo apt-get install python2.7

python is very likely to already be installed on your system.

(Optional, but recommended) If you wish to use avahi (bonjour) for advertising the server so that
you can do automatic discovery of the ip address and port for VMXProxy...

    sudo apt-get install avahi-daemon avahi-utils
    sudo update-rc.d avahi-daemon defaults
    sudo /etc/init.d/avahi-daemon restart

Get the VMXProxy code itself...

    cd $HOME
    git clone https://bitbucket.org/JamesCC/vmxproxypy.git
 
VMXProxy has a python module dependency on pyserial.  In most cases this will have already been 
installed as part of python, but you can check (and install) by...

    pip install pyserial
    
You can now run the script using...

    cd vmxproxypy
    python2 VMXProxy --help

You must run the script from this directory, as VMXProxy expects to find simrc.txt in the current
directory.


### Installing as a linux service

The VMXProxy.initrc file is used, in conjunction with `screen` to create a service which will run
(in the background) at bootup.

If you wish to install the script as a service, you must first edit the VMXProxy.initrc file to
pass the correct parameters to the VMXProxy python script.

    nano VMXProxy.initrc

Look for the "Starting VMXProxy" line and uncomment if you want the simulations and adjust any
port numbers.  Make sure you serial port is attached (if using a USB to serial port adapter).  If
you are under any doubt as to what it might be instantiated as (/dev/ttyUSB0 is not unusual), 
disconnect it, reconnect it and type... `dmesg`.  In the last dozen or so lines it will indicate
the dev name for the USB Serial Port connection.

Now install the service...

    sudo apt-get install screen
    sudo make install                           # install service
    sudo /etc/init.d/VMXProxyStartup start      # start service

You can query the state of the service...

    sudo /etc/init.d/VMXProxyStartup status

And attach to the listed screen sessions for purposes of debugging...
   
    sudo screen -r <NUMBER_PREFIX_FROM_STATUS_LIST>

Once attached... Ctrl A, Ctrl D detaches and Ctrl A, Ctrl K kills.

You can stop it (but leaves service still installed)...

    sudo /etc/init.d/VMXProxyStartup stop

And you remove (uninstall) it by...

    sudo rm /etc/init.d/VMXProxyStartup


### Installing on a Raspberry Pi

I have had great success in following the above instructions for a standard Raspberry Pi linux
install.  The original Raspberry Pi is more than powerful enough.

This is a very cheap (~£30) mini computer which runs linux.  With a serial port adapter and a USB 
power supply it becomes your very own terminal adapter for the V-Mixer.  Unless you buy a wifi 
dongle, you will need to connect it to your wireless router via an ethernet cable.  

See <http://www.raspberrypi.org/> for more info.

I used the Raspbian "Wheezy" linux install.  Once that is in place you can just follow the 
instructions for linux above to install and get a service running (you won't need to install
git or python as they will already be installed).

The Raspberry Pi boots within 20 seconds, and needs no user interaction, so can be boxed and left
to be powered up and down with the mixer.


### Upgrading

If you are running linux, the following will upgrade your installation...

    cd $HOME/vmxproxypy
    git pull

If you are running windows, just download a new copy from the website, unzip it and copy in your 
passcodes.txt and simrc.txt files from your old installation before you delete it.

---
JamesCC @ 06jun15
