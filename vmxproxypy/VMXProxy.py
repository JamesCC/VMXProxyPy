#! /usr/bin/env python

"""A program to provide a simulator and networked proxy service for Roland's
VMixer serial protocol."""

#    This file is part of VMXProxyPy.
#
#    VMXProxyPy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    VMXProxyPy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Less General Public License
#    along with VMXProxyPy.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import optparse
import threading
import SocketServer
import os
import time

from vmxproxypy.VMXSimFileParser import VMXSimFileParser
from vmxproxypy.VMXSerialPort import VMXSerialPort
from vmxproxypy.VMXProcessor import VMXProcessor
from vmxproxypy.VMXParser import VMXParser

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    """Handler container for incoming TCP connections"""

    def handle(self):
        """Handler for incoming TCP connections"""
        address = self.request.getsockname()
        logging.info( "Connected to " + address[0] + address[1] )
        authenticated = (PASSWORD is None)
        tcp_input_gatherer = VMXParser()
        try:
            data = self.request.recv(1024)
            while data:
                tcp_command = tcp_input_gatherer.process(data)
                while tcp_command:
                    if authenticated:
                        response = CMD_PROCESSOR.process(tcp_command)
                    elif tcp_command == chr(2)+"###PWD:"+PASSWORD+";":
                        response = chr(6)
                        authenticated = 1
                    else:
                        logging.warning("Not Authenticated")
                        response = chr(2)+"ERR:6;"  
                    if response != "":
                        self.request.sendall(response)
                    tcp_command = tcp_input_gatherer.process()
                data = self.request.recv(1024)
        except:
            pass
        logging.info( "Disconnected from " + address[0] + address[1] )

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """Instance of a TCP Server that can handle multiple simultaneous 
    connections."""
    pass



SERIAL    = None
BAUD      = 115200
HOST      = ""
PORT      = 10000
PASSWORD  = None
SIMFILERC = "simrc.txt"
VERBOSITY = logging.INFO

CMD_PROCESSOR = VMXProcessor()    


def parse_parameters():
    """Parse the command line parameters and alter any global variables to
    reflect the configuration."""
    
    global SERIAL
    global BAUD
    global PORT
    global PASSWORD
    global VERBOSITY
    
    parser = optparse.OptionParser(usage="""\
%prog [options]

Roland VMixer interface adaptor.  It can run in three modes.

 1. Provide a network serial interface, specifically to handle the Roland
    VMixer protocol.  (-s and -n options supplied)
 2. Provide an emulation of a VMixer over the network.  (if no -s option)
 3. Provide an emulation of a VMixer over serial.  (if no -n option)""")

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
        help="quiet mode", default=False)

    parser.add_option("-v", "--verbose", dest="verbosity", action="store_true",
        help="show debug", default=False)

    parser.add_option("-s", "--serial", dest="serial",
        help="use serial port as proxy", default=None, metavar="SERIAL")

    parser.add_option("-b", "--baud", dest="baud",
        help="serial port baud rate", default=BAUD, metavar="BAUD")

    parser.add_option("-n", "--net", dest="port",
        help="set PORT for network", default=None, metavar="PORT")

    parser.add_option("-p", "--password", dest="password",
        help="set password authentication", default=None, metavar="PASSWD")

    (options, args) = parser.parse_args()

    SERIAL    = options.serial
    BAUD      = options.baud
    PORT      = options.port
    PASSWORD  = options.password

    if options.quiet:           # just warnings and errors
        VERBOSITY = logging.WARNING
    elif options.verbosity:     # debug output
        VERBOSITY = logging.DEBUG
    else:                       # normal output
        VERBOSITY = logging.INFO


def main():
    """The main program setting up required objects, network server interface,
    serial port interface dependent on the configuration."""
    logging.basicConfig(format='%(asctime)s.%(msecs)03d:%(threadName)s:%(levelname)s - %(message)s', datefmt='%H%M%S', 
                        level=VERBOSITY)

    if SERIAL is not None:
        serial_port = VMXSerialPort( SERIAL, int(BAUD) )
        logging.info("Opened Serial Port %s at %s baud", SERIAL, BAUD)

    # proxy mode is only available if both network and serial are declared
    if SERIAL is not None and PORT is not None:
        logging.info("Proxy Mode")
    else:
        logging.info("Simulation Mode")
        VMXSimFileParser(CMD_PROCESSOR).read_file(SIMFILERC)

    if PASSWORD is not None:
        logging.info("Password is set - Authentication will be required")

    if PORT is not None:
        # Input is from Network
        server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)
        ip_addr, port = server.server_address
        logging.info("Network Server started on port %d", port)

        if SERIAL is not None:
            CMD_PROCESSOR.set_mixer_interface(serial_port)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        logging.info("Server loop running in thread: " + server_thread.name)
        
        try:
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            server.shutdown()
            logging.info("Server shutdown")
            if SERIAL is not None:
                del serial_port
                logging.info("Serial Port shutdown")
            os._exit(0)

    elif SERIAL is not None:        # (and PORT is None)
        # Input is from Serial Port
        logging.info("Mixer Emulation - expecting input from Serial Port")
        try:
            to_serial = ""
            serial_input_gatherer = VMXParser()
            while True:
                from_serial = serial_port.process(to_serial)
                to_serial = ""
                serial_command = serial_input_gatherer.process(from_serial)
                while serial_command:
                    to_serial += CMD_PROCESSOR.process(serial_command)
                    serial_command = serial_input_gatherer.process()

        except KeyboardInterrupt:
            del serial_port
            logging.info("Serial Port shutdown")
            os._exit(0)
    
    else:
        logging.error("Invalid mode.  Need either or both -s or -n options.")


if __name__ == "__main__":
    parse_parameters()
    main()
