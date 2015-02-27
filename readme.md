# Python VMXProxy

<https://bitbucket.org/JamesCC/vmxproxypy>
<https://sites.google.com/site/vmxserialremote/>


## Introduction

A network to serial terminal server optimised for connection to Roland V-Mixer mixing consoles.  
Intended to be used with VMX Serial Remote Android App.

It is ruby script, runs under Linux, Windows and (potentially) OSX.

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

The heart of VMXProxy is a Python script.  It accepts command line parameters.

	> python vmxproxypy/VMXProxy.py -h
	Usage: VMXProxy.py [options]

	Roland VMixer interface adaptor.  It can run in three modes.

	 1. Provide a network serial interface, specifically to handle the Roland
		VMixer protocol.  (-s and -n options supplied)
	 2. Provide an emulation of a VMixer over the network.  (if no -s option)
	 3. Provide an emulation of a VMixer over serial.  (if no -n option)

	Options:
	  -h, --help            show this help message and exit
	  -q, --quiet           quiet mode
	  -v, --verbose         show debug
	  -s SERIAL, --serial=SERIAL
							use serial port as proxy
	  -b BAUD, --baud=BAUD  serial port baud rate
	  -n PORT, --net=PORT   set PORT for network
	  -p PASSWD, --password=PASSWD
							set password authentication

Example startup scripts are available, start_sim.bat and start_proxy.bat for windows users, 
start_sim.sh and start_proxy.sh for unix users.


## Get me started Quickly!

todo


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

On the ARGS line after add a password argument...

	ARGS: --net=10000 --serial=COM1 --password=HiPPY    # Proxy forwarding Network port 10000 to Windows serial port COM1

This is specifying HiPPY as the password.  Don't use spaces, the case of letters matters.  Make 
sure VMX Serial Remote is setup to use the same password.

The password mechanism is only intended as a basic defence against network hacks.  As you can see
the password is stored in the clear and can be easily compromised if someone has access to the 
computer/device running VMXProxy.


## Installing under Linux

### Basic environment

todo


### Intalling as a linux service

todo

### Installing on a Raspberry Pi

I have had great success in following the above instructions for a standard Raspberry Pi linux
install.

This is a very cheap (£35) mini computer which runs linux.  With a serial port adapter and a USB 
power supply it becomes your very own terminal adapter for the V-Mixer.  Unless you buy a wifi 
dongle, you will need to connect it to your wireless router via an ethernet cable.  

See <http://www.raspberrypi.org/> for more info.

I used the Raspbian "Wheezy" linux install.  Once that is in place you can just follow the 
instructions for linux above to install and get a service running.

The Raspberry Pi boots within 20seconds, and needs no user interaction, so can be boxed and left
to be powered up and down with the mixer.


### Maintainance under linux (or Raspberry Pi)

To update your installation you just need to give the following commands in the directory which
performed `git clone` to create...

    sudo /etc/init.d/VMXProxyStartup stop
    git pull
    sudo /etc/init.d/VMXProxyStartup start

If you are updating a Raspberry Pi buried behind a desk, you can get android apps to ssh into 
the Raspberry Pi meaning you can remotely update it.  I use "JuiceSSH" (see google play).  You
can use "Bonjour Browser" to find its ip address if you installed avahi.


## Installing under Windows

todo

Install python2.7
https://pip.pypa.io/en/latest/installing.html download get-pip.py
python get-pip.py
add in C:\Python27\Lib\mimetypes.py line 260
					if '\0' in subkeyname: # new
						print "Skipping bad key: %s" % subkeyname # new
						continue # new
pip install serialpy



JamesCC @ 27feb2015