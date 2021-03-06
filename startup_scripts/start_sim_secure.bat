@echo off

rem ***********************************************************************************************
rem   Roland VMixer interface adaptor.  It can run in three modes.
rem
rem    1. Provide a network serial interface, specifically to handle the Roland
rem       VMixer protocol  (--serial and --net options supplied)
rem    2. Provide an emulation of a VMixer over the network  (if no --serial option)
rem    3. Provide an emulation of a VMixer over serial  (if no --net option)
rem
rem   Options:
rem     -h, --help            show this help message and exit
rem     -q, --quiet           quiet mode
rem     -v, --verbose         show debug
rem     -s PORT, --serial=PORT
rem                           use serial port as proxy
rem     -b BAUD, --baud=BAUD  serial port baud rate
rem     -n PORT, --net=PORT   set host_port_number for network
rem     -p FILE, --passcodefile=FILE
rem                           use passcode authentication
rem     -z MS, --delay=MS     (debug) set random delay
rem     -x X, --discard=X     (debug) set discard rate
rem ***********************************************************************************************

cd %~dp0..
call start_VMXProxy.bat -v --net=10000 --passcodefile=passcodes.txt