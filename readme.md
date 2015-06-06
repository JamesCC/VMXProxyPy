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

    Where $ is the character code 0x02, and CMD is a three letter command code
    I1 represents the input
    p1, p2 are two parameters (exact number depends on the cmd)
    All commands are terminated by a semicolon.

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

When concatenating commands it is important to avoid any commands that respond with ACKs (i.e. 
only concatenate query commands).  This is to avoid confusing the application as to which command
is being acknowledged (since an ACK returns no context information).

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

Windows users can use an executable, which is a wrapped version of this script, hiding all this
detail.



## Initialisation Files





## Get me started Quickly!

Okay if you want to get something going fast best go for the Windows installer

### Prebuild Executable for Windows

First get the latest installer.  This can be found on the website...
<https://sites.google.com/site/vmxserialremote/>

The installer will install all that is needed, without you needing to download ruby, ruby dev 
kits, gems, etc.  After installing you will need to then alter the VMXProxy.ini to give the 
settings, before running.

After the install completes, the ini file will be opened.  Uncomment the Proxy forwarding line for
windows (notice missing # at start of the line)...

	# uncomment one of the following (first detected takes precedence)
	#ARGS: --network 10000                              # Simulator on Network port 10000
	#ARGS: --serial COM1                                # Simulator on Windows serial port COM1
	#ARGS: --serial /dev/ttyUSB0                        # Simulator on Linux serial port ttyUSB0
	ARGS: --network 10000 --serial COM1                # Proxy forwarding Network port 10000 to Windows serial port COM1
	#ARGS: --network 10000 --serial /dev/ttyUSB0        # Proxy forwarding Network port 10000 to Linux serial port ttyUSB0
	
	# otherwise you'll just get the help...
	ARGS: --help
	
You may need to alter the COM port number and network port number.  You'll also need to make note
of the ip address of the computer (you'll need to set this in the settings for the Android App 
VMX Serial Remote).

To automatically start VMXProxy at bootup, copy the startup icon on the desktop into the "Startup"
folder in Start Menu -> All Programs.


### Automatic Discovery

If you use the "Search for Server" option in the VMX Serial Remote App, you will need to install 
Apple's Bonjour (if running in Windows).  Linux system uses the equivalent called avahi.  This 
allows VMXProxy to advertise its ip address and port number.

Bonjour is used in a wide variety of places, not just Apple products.  If you don't have it 
installed (check Control Panel / Program and Features), the simplest method is to get it is to 
install iTunes.

I full understand if you might not want to do that.  You can install just Bonjour by itself by
downloading the itunes installer from http://www.apple.com/uk/itunes/ and using winrar or 7zip 
to unpack the executable (yes you can do that).  Look for... .rsrc/RCDATA/CABINET and repeat 
the unpack operation.  In there  you'll find Bonjour.msi.  Double click to install this 
independently.


### Securing with a Password

On the ARGS line after add a password arguement...

	ARGS: --network 10000 --serial COM1 --password HiPPY    # Proxy forwarding Network port 10000 to Windows serial port COM1

This is specifying HiPPY as the password.  Don't use spaces, the case of letters matters.  Make 
sure VMX Serial Remote is setup to use the same password.

The password mechanism is only intended as a basic defence agains network hacks.  As you can see
the password is stored in the clear and can be easily compromised if someone has access to the 
computer/device running VMXProxy.



## Installing under Linux

### Basic environment

You will need root privaledges.  For Fedora replace `apt-get` with `yum`

    sudo apt-get update
    sudo apt-get install git
    sudo apt-get install ruby
    sudo apt-get install ruby-dev
    sudo apt-get install rake
    sudo gem install os

(Optional, but recommended) If you wish to use avahi (bonjour) for advertising the server so that
you can do automatic discovery of the ip address and port for VMXProxy...

    sudo apt-get install avahi-daemon avahi-utils
    sudo update-rc.d avahi-daemon defaults
    sudo /etc/init.d/avahi-daemon restart

Get the VMXProxy code itself...

    cd $HOME
    git clone https://bitbucket.org/JamesCC/vmxproxy.git
 
Install gems required for VMXProxy...
    
    sudo rake geminstall

You can now run the script using...

    ruby VMXProxy.rb --help

To save you typing there are some convenience rake targets prefixed with `run`.  See those by 
typing...  `rake`


### Intalling as a linux service

The VMXProxy.initrc file is used, in conjunction with `screen` to create a service which will run
(in the background) at bootup.

If you wish to install the script as a service, you must first edit the VMXProxy.initrc file to
use the correct parameters.

    nano VMXProxy.initrc

Look for the "Starting VMXProxy" line and uncomment if you want the simulations and adjust any
port numbers.  Make sure you serial port is attached (if using a USB to serial port adapter).  If
you are under any doubt as to what it might be instantiated as (/dev/ttyUSB0 is not unusual), 
disconnect it, reconnect it and type... `dmesg`.  In the last douzen or so lines it will indicate
the dev name for the USB Serial Port connection.

Now install the service...

    sudo apt-get install screen
    sudo rake install                           # install service
    sudo /etc/init.d/VMXProxyStartup start      # start service

You can query the state of the service...

    sudo /etc/init.d/VMXProxyStartup status

And attach to the listed screen sessions for purposes of debugging...
   
    sudo screen -r <NUMBER_PREFIX_FROM_STATUS_LIST>

Once attached... Ctrl A, Ctrl D detaches and Ctrl A, Ctrl K kills.

You can stop it (but leaves service still installed)...

    sudo /etc/init.d/VMXProxyStartup stop

Finally you remove it by...

    sudo rake uninstall


### Installing on a Raspberry Pi

I have had great success in following the above instructions for a standard Raspberry Pi linux
install.  The original Raspberry Pi is more than powerful enough.

This is a very cheap (~£30) mini computer which runs linux.  With a serial port adapter and a USB 
power supply it becomes your very own terminal adapter for the V-Mixer.  Unless you buy a wifi 
dongle, you will need to connect it to your wireless router via an ethernet cable.  

See <http://www.raspberrypi.org/> for more info.

I used the Raspbian "Wheezy" linux install.  Once that is in place you can just follow the 
instructions for linux above to install and get a service running.

The Raspberry Pi boots within 20seconds, and needs no user interaction, so can be boxed and left
to be powered up and down with the mixer.


JamesCC @ 06jun15