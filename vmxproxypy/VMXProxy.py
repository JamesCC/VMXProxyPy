#! /usr/bin/env python

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
import socket
import threading
import SocketServer
import os
import time

from VMXSimFileParser import VMXSimFileParser
from VMXSerialPort import VMXSerialPort
from VMXProcessor import VMXProcessor
from VMXParser import VMXParser

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    # note: self.server is an instance of class ThreadedTCPServer
    #       self.request is an instance of class socket
    def handle(self):
        address = self.request.getsockname();
        print "Connected to ", address[0], address[1]
        authenticated = (self.server.password is None)
        inputGatherer = VMXParser();
        try:
            data = self.request.recv(1024)
            while data:
                command = inputGatherer.process(data)
                while command:
                    if authenticated:
                        response = self.server.cmdProcessor.process(command)
                    elif command == chr(2)+"###PWD:"+self.server.password+";":
                        response = chr(6)
                        authenticated = 1
                    else:
                        logging.warning("Not Authenticated")
                        response = chr(2)+"ERR:6;"  
                    if response != "":
                        self.request.sendall(response)
                    command = inputGatherer.process()
                data = self.request.recv(1024)
        except:
            pass
        print "Disconnected from ", address[0], address[1]

        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def startServer(self, cmdProcessor, password):
        ip, port = self.server_address
        logging.info("Network Server started on port %d" % port)
        self.cmdProcessor = cmdProcessor
        self.password = password
        
        if password is not None:
            logging.info("Password is set - Authentication will be required")

        self.serve_forever()


def VMXProxy( SERIAL=None, BAUD=115200, HOST="", PORT=None, PASSWORD=None, VERBOSITY=logging.INFO, 
              SIMFILERC=os.path.dirname(os.path.abspath(__file__))+"/../simrc.txt" ):

    logging.basicConfig(format='%(asctime)s.%(msecs)03d:%(threadName)s:%(levelname)s - %(message)s', 
                        datefmt='%H%M%S', level=VERBOSITY)
                        
    cmdProcessor = VMXProcessor()
    
    if SERIAL is not None:
        serialPort = VMXSerialPort( SERIAL, int(BAUD) )
        logging.info("Opened Serial Port %s at %s baud" % (SERIAL, BAUD))

    # proxy mode is only available if both network and serial are declared
    if SERIAL is not None and PORT is not None:
        logging.info("Proxy Mode")
    else:
        logging.info("Simulation Mode")
        VMXSimFileParser(cmdProcessor).ReadFile(SIMFILERC)

    if PORT is not None:
        # Input is from Network
        server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)

        if SERIAL is not None:
            cmdProcessor.setMixerIO(serialPort)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.startServer, args=(cmdProcessor, PASSWORD) )
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        
        try:
            while True:
                # do nothing waiting for a keyboard interrupt
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
            del cmdProcessor
            logging.info("Server shutdown")
            if SERIAL is not None:
                del serialPort
                logging.info("Serial Port shutdown")
            os._exit(0)

    elif SERIAL is not None:        # (and PORT is None)
        # Input is from Serial Port
        logging.info("Mixer Emulation - expecting input from Serial Port")
        try:
            toSerial = ""
            inputGatherer = VMXParser();
            while True:
                fromSerial = serialPort.process(toSerial)
                toSerial = ""
                command = inputGatherer.process(fromSerial)
                while command:
                    toSerial += cmdProcessor.process(command)
                    command = inputGatherer.process()

        except KeyboardInterrupt:
            pass
        finally:
            del cmdProcessor
            del serialPort
            logging.info("Serial Port shutdown")
            os._exit(0)
    
    else:
        logging.error("Invalid mode.  Need either or both -s or -n options.")


def main():
    parser = optparse.OptionParser(usage="""\
%prog [options]

Roland VMixer interface adaptor.  It can run in three modes.

 1. Provide a network serial interface, specifically to handle the Roland
    VMixer protocol.  (-s and -n options supplied)
 2. Provide an emulation of a VMixer over the network.  (if no -s option)
 3. Provide an emulation of a VMixer over serial.  (if no -n option)""")

    parser.add_option("-q", "--quiet", dest="QUIET", action="store_true",
        help="quiet mode", default=False)

    parser.add_option("-v", "--verbose", dest="VERBOSITY", action="store_true",
        help="show debug", default=False)

    parser.add_option("-s", "--serial", dest="SERIAL",
        help="use serial port as proxy", default=None, metavar="SERIAL")

    parser.add_option("-b", "--baud", dest="BAUD",
        help="serial port baud rate", default=115200, metavar="BAUD")

    parser.add_option("-n", "--net", dest="PORT",
        help="set PORT for network", default=None, metavar="PORT")

    parser.add_option("-p", "--password", dest="PASSWORD",
        help="set password authentication", default=None, metavar="PASSWD")

    (options, args) = parser.parse_args()

    if options.QUIET:           # just warnings and errors
        verbosity = logging.WARNING
    elif options.VERBOSITY:     # debug output
        verbosity = logging.DEBUG
    else:                       # normal output
        verbosity = logging.INFO

    # Start VMXProxy
    VMXProxy( SERIAL=options.SERIAL, BAUD=options.BAUD, PORT=options.PORT, PASSWORD=options.PASSWORD, VERBOSITY=verbosity )

if __name__ == "__main__":
    main()