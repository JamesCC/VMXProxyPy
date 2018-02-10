#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Main entry point for zip and directory usage of python interpretor startup."""

import os
import logging
import argparse
from . import __version__
from .VMXProxy import vmx_proxy
from .VMXProxyGUI import start_gui

def main():
    """Main entry point, handles parameter parsing."""
    parser = argparse.ArgumentParser(prog="VMXProxy",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""\
Roland VMixer interface adaptor.  It can run in three modes.\n

 1. Provide a network serial interface, specifically to handle the Roland
    VMixer protocol  (--serial and --net options supplied)
 2. Provide an emulation of a VMixer over the network  (if no --serial option)
 3. Provide an emulation of a VMixer over serial  (if no --net option)""")

    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                      help="quiet mode", default=False)

    parser.add_argument("-v", "--verbose", dest="verbosity", action="store_true",
                      help="show debug", default=False)

    parser.add_argument("-s", "--serial", dest="serial",
                      help="use serial port as proxy", default=None, metavar="PORT")

    parser.add_argument("-b", "--baud", dest="baud",
                      help="serial port baud rate", default=115200, metavar="BAUD")

    parser.add_argument("-n", "--net", dest="port",
                      help="set host_port_number for network", default=None, metavar="PORT")

    parser.add_argument("-p", "--passcodefile", dest="passcodefile",
                      help="use passcode authentication", default=None, metavar="FILE")

    parser.add_argument("-z", "--delay", dest="debug_cmd_delay",
                      help="(debug) set random delay", default=None, metavar="MS")

    parser.add_argument("-x", "--discard", dest="debug_discard_rate",
                      help="(debug) set discard rate", default=None, metavar="X")

    parser.add_argument("--version", dest="version", action="store_true",
                      help="show version", default=False)

    parser.add_argument("-g", "--gui", dest="gui", action="store_true",
                      help="show GUI for altering configuration", default=False)

    args = parser.parse_args()

    if args.version:
        print(__version__)
        os._exit(0)

    if args.gui:
        updated_options = start_gui(args)
        if not updated_options:
            os._exit(0)

    if args.quiet:           # just warnings and errors
        verbosity = logging.WARNING
    elif args.verbosity:     # debug output
        verbosity = logging.DEBUG
    else:                       # normal output
        verbosity = logging.INFO

    # Start VMXProxy
    vmx_proxy(serial_port_name=args.serial, baudrate=args.baud,
              host_port_number=args.port, server_passcodefile=args.passcodefile,
              debug_cmd_delay=args.debug_cmd_delay, debug_discard_rate=args.debug_discard_rate,
              verbosity=verbosity)

    os._exit(0)

if __name__ == "__main__":
    main()
