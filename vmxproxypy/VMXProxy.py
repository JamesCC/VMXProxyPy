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
import threading
import SocketServer
import os
import time
import select
import sys
import pybonjour


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
        tcp_input_gatherer = VMXParser();
        try:
            data = self.request.recv(1024)
            while data:
                command = tcp_input_gatherer.process(data)
                while command:
                    if authenticated:
                        response = self.server.cmd_processor.process(command)
                    elif command == chr(2)+"###PWD:"+self.server.password+";":
                        response = chr(6)
                        authenticated = 1
                    else:
                        logging.warning("Not Authenticated")
                        response = chr(2)+"ERR:6;"  
                    if response != "":
                        self.request.sendall(response)
                    command = tcp_input_gatherer.process()
                data = self.request.recv(1024)
        except:
            pass
        print "Disconnected from ", address[0], address[1]

        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def startServer(self, cmd_processor, password):
        ip, port = self.server_address
        logging.info("Network Server started on port %d" % port)
        self.cmd_processor = cmd_processor
        self.password = password
        
        if password is not None:
            logging.info("Password is set - Authentication will be required")

        self.serve_forever()


def register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        logging.info("Registered service with Bonjour/AVAHI")
        
def VMXProxy( SERIAL=None, BAUD=115200, HOST="", PORT=None, PASSWORD=None, VERBOSITY=logging.INFO, 
              DEBUG_CMD_DELAY=None, DEBUG_DISCARD_RATE=None,
              SIMFILERC=os.path.dirname(os.path.abspath(__file__))+"/../simrc.txt" ):

    logging.basicConfig(format='%(asctime)s.%(msecs)03d:%(threadName)s:%(levelname)s - %(message)s', 
                        datefmt='%H%M%S', level=VERBOSITY)
                        
    cmd_processor = VMXProcessor()
    
    if SERIAL is not None:
        serial_port = VMXSerialPort( SERIAL, int(BAUD) )
        logging.info("Opened Serial Port %s at %s baud" % (SERIAL, BAUD))

    # proxy mode is only available if both network and serial are declared
    if SERIAL is not None and PORT is not None:
        logging.info("Proxy Mode")
    else:
        logging.info("Simulation Mode")
        VMXSimFileParser(cmd_processor).read_file(SIMFILERC)

    if DEBUG_DISCARD_RATE is not None:
        logging.info("Debug Mode - Randomly discard 1 in %s commands", DEBUG_DISCARD_RATE)
        cmd_processor.set_debug_discard_rate( int(DEBUG_DISCARD_RATE) )
    
    if DEBUG_CMD_DELAY is not None:
        logging.info("Debug Mode - Randomly delay up to %sms", DEBUG_CMD_DELAY)
        cmd_processor.set_debug_cmd_delay_in_ms( int(DEBUG_CMD_DELAY) )

    if PORT is not None:
        # Input is from Network
        server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)

        if SERIAL is not None:
            cmd_processor.set_mixer_interface(serial_port)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.startServer, args=(cmd_processor, PASSWORD) )
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        txt_record = pybonjour.TXTRecord({'vmxproxy':1});
        sdRef = pybonjour.DNSServiceRegister(name = "vmxproxy",
                                             regtype = "_telnet._tcp",
                                             port = int(PORT),
                                             txtRecord = txt_record,
                                             callBack = register_callback)
        
        try:
            while True:
                # do nothing waiting for a keyboard interrupt
                ready = select.select([sdRef], [], [])
                if sdRef in ready[0]:
                    pybonjour.DNSServiceProcessResult(sdRef)
                
        except KeyboardInterrupt:
            pass
        finally:
            sdRef.close()
            server.shutdown()
            del cmd_processor
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
            tcp_input_gatherer = VMXParser();
            while True:
                fromSerial = serial_port.process(to_serial)
                to_serial = ""
                command = tcp_input_gatherer.process(fromSerial)
                while command:
                    to_serial += cmd_processor.process(command)
                    command = tcp_input_gatherer.process()

        except KeyboardInterrupt:
            pass
        finally:
            del cmd_processor
            del serial_port
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

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
        help="quiet mode", default=False)

    parser.add_option("-v", "--verbose", dest="verbosity", action="store_true",
        help="show debug", default=False)

    parser.add_option("-s", "--serial", dest="serial",
        help="use serial port as proxy", default=None, metavar="SERIAL")

    parser.add_option("-b", "--baud", dest="baud",
        help="serial port baud rate", default=115200, metavar="BAUD")

    parser.add_option("-n", "--net", dest="port",
        help="set PORT for network", default=None, metavar="PORT")

    parser.add_option("-p", "--password", dest="password",
        help="set password authentication", default=None, metavar="PASSWD")

    parser.add_option("-z", "--delay", dest="debug_cmd_delay",
        help="(debug) set random delay", default=None, metavar="MS")

    parser.add_option("-x", "--discard", dest="debug_discard_rate",
        help="(debug) set discard rate", default=None, metavar="X")

    (options, args) = parser.parse_args()

    if options.quiet:           # just warnings and errors
        verbosity = logging.WARNING
    elif options.verbosity:     # debug output
        verbosity = logging.DEBUG
    else:                       # normal output
        verbosity = logging.INFO

    # Start VMXProxy
    VMXProxy( SERIAL=options.serial, BAUD=options.baud, PORT=options.port, PASSWORD=options.password, 
              DEBUG_CMD_DELAY=options.debug_cmd_delay, DEBUG_DISCARD_RATE=options.debug_discard_rate, 
              VERBOSITY=verbosity )

if __name__ == "__main__":
    main()