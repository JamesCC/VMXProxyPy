# -*- coding: utf-8 -*-

"""Statup script for the VMXProxy application.   Startup defaults are configured here which will
be used if no parameters are passed."""

import sys
import runpy

# usage: VMXProxy [-h] [-q] [-v] [-s PORT] [-b BAUD] [-n PORT] [-p FILE] [-z MS]
#                 [-x X] [--version] [-g]
#
# Roland VMixer interface adaptor.  It can run in three modes.
#
#  1. Provide a network serial interface, specifically to handle the Roland
#     VMixer protocol  (--serial and --net options supplied)
#  2. Provide an emulation of a VMixer over the network  (if no --serial option)
#  3. Provide an emulation of a VMixer over serial  (if no --net option)
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -q, --quiet           quiet mode
#   -v, --verbose         show debug
#   -s PORT, --serial PORT
#                         use serial port as proxy
#   -b BAUD, --baud BAUD  serial port baud rate
#   -n PORT, --net PORT   set host_port_number for network
#   -p FILE, --passcodefile FILE
#                         use passcode authentication
#   -z MS, --delay MS     (debug) set random delay
#   -x X, --discard X     (debug) set discard rate
#   --version             show version
#   -g, --gui             show GUI for altering configuration

###############################################################################################
# DEAULT USER OPTIONS

# Replace True with False to prevent GUI being displayed (GUI allows further altering settings)
START_GUI_IF_NO_OPTIONS = True

# uncomment one of the DEFAULT_OPTIONS following by removing a # (hash at the start)
#
#   sim mode                - lets you test the Android App without a mixer without needing passcodes
#   sim mode with passcode  - lets you test the Android App without a mixer without a passcode (default is 9876)
#   proxy mode              - is what you'll use when you want the App to communicate to the mixer
#   mixer emulation mode    - is for debug
#
# or set your own DEFAULT_OPTIONS using the usage information above.

DEFAULT_OPTIONS = "VMXProxy --net=10000"                                   # sim mode
#DEFAULT_OPTIONS = "VMXProxy --net=10000 --passcodefile=passcodes.txt"      # sim mode with passcodes
#DEFAULT_OPTIONS = "VMXProxy --net=10000 --serial=COM1"                     # proxy mode
#DEFAULT_OPTIONS = "VMXProxy --serial=COM1"                                 # (debug) mixer emulation mode

###############################################################################################

# if no command arguments (call in a default configuration)
if len(sys.argv) == 1:
    print("No parameters have been given so DEFAULT_OPTIONS from %s are being used." % __file__)
    sys.argv = DEFAULT_OPTIONS.split()
    if START_GUI_IF_NO_OPTIONS:
        sys.argv.append("-g")

if __name__ == "__main__":
    runpy.run_module("VMXProxy", run_name="__main__")
