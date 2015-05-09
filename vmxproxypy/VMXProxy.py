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
import select
import pybonjour


from VMXSimFileParser import VMXSimFileParser
from VMXSerialPort import VMXSerialPort
from VMXProcessor import VMXProcessor
from VMXParser import VMXParser

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    """Handler container for incoming TCP connections"""

    # note: self.server is an instance of class ThreadedTCPServer
    #       self.request is an instance of class socket
    def handle(self):
        address = self.request.getsockname()
        print "Connected to ", address[0], address[1]
        authenticated = (self.server.password is None)
        tcp_input_gatherer = VMXParser()
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
    """Instance of a TCP Server that can handle multiple simultaneous
    connections."""

    def start_server(self, cmd_processor, password=None):
        """Start the server with the supplied command processor object for handling incoming
        commands."""
        _, port = self.server_address
        logging.info("Network Server started on port %d", port)
        self.cmd_processor = cmd_processor
        self.password = password

        if password is not None:
            logging.info("Password is set - Authentication will be required")

        self.serve_forever()


def register_callback(sd_ref, flags, error_code, name, regtype, domain):
    """Callback used to report success when starting up Bonjour/AVAHI."""
    _ = sd_ref
    _ = flags
    _ = name
    _ = regtype
    _ = domain
    if error_code == pybonjour.kDNSServiceErr_NoError:
        logging.info("Registered service with Bonjour/AVAHI")

def vmx_proxy(serial_port_name=None, baudrate=115200,
              host_ip="", host_port_number=None, server_password=None,
              debug_cmd_delay=None, debug_discard_rate=None,
              simfilerc=os.path.dirname(os.path.abspath(__file__))+"/../simrc.txt", verbosity=logging.INFO):
    """Start the vmx_proxy server / simulator"""

    logging.basicConfig(format='%(asctime)s.%(msecs)03d:%(threadName)s:%(levelname)s - %(message)s',
                        datefmt='%H%M%S', level=verbosity)

    cmd_processor = VMXProcessor()

    if serial_port_name is not None:
        serial_port = VMXSerialPort(serial_port_name, int(baudrate))
        logging.info("Opened Serial Port %s at %s baud", serial_port_name, baudrate)

    # proxy mode is only available if both network and serial are declared
    if serial_port_name is not None and host_port_number is not None:
        logging.info("Proxy Mode")
    else:
        logging.info("Simulation Mode")
        VMXSimFileParser(cmd_processor).read_file(simfilerc)

    if debug_discard_rate is not None:
        logging.info("Debug Mode - Randomly discard 1 in %s commands", debug_discard_rate)
        cmd_processor.set_debug_discard_rate(int(debug_discard_rate))

    if debug_cmd_delay is not None:
        logging.info("Debug Mode - Randomly delay up to %sms", debug_cmd_delay)
        cmd_processor.set_debug_cmd_delay_in_ms(int(debug_cmd_delay))

    if host_port_number is not None:
        # Input is from Network
        server = ThreadedTCPServer((host_ip, int(host_port_number)), ThreadedTCPRequestHandler)

        if serial_port_name is not None:
            cmd_processor.set_mixer_interface(serial_port)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.start_server, args=(cmd_processor, server_password))
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        txt_record = pybonjour.TXTRecord({'vmxproxy':1})
        sd_ref = pybonjour.DNSServiceRegister(name="vmxproxy", regtype="_telnet._tcp",
                                              port=int(host_port_number), txtRecord=txt_record,
                                              callBack=register_callback)

        try:
            while True:
                # do nothing waiting for a keyboard interrupt
                ready = select.select([sd_ref], [], [])
                if sd_ref in ready[0]:
                    pybonjour.DNSServiceProcessResult(sd_ref)

        except KeyboardInterrupt:
            pass
        finally:
            sd_ref.close()
            server.shutdown()
            del cmd_processor
            logging.info("Server shutdown")
            if serial_port_name is not None:
                del serial_port
                logging.info("Serial Port shutdown")
            os._exit(0)

    elif serial_port_name is not None:        # (and host_port_number is None)
        # Input is from Serial Port
        logging.info("Mixer Emulation - expecting input from Serial Port")
        try:
            to_serial = ""
            tcp_input_gatherer = VMXParser()
            while True:
                from_serial = serial_port.process(to_serial)
                to_serial = ""
                command = tcp_input_gatherer.process(from_serial)
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
    """Main entry point, handles parameter parsing."""
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
                      help="use serial port as proxy", default=None, metavar="PORT")

    parser.add_option("-b", "--baud", dest="baud",
                      help="serial port baud rate", default=115200, metavar="BAUD")

    parser.add_option("-n", "--net", dest="port",
                      help="set host_port_number for network", default=None, metavar="PORT")

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
    vmx_proxy(serial_port_name=options.serial, baudrate=options.baud,
              host_port_number=options.port, server_password=options.password,
              debug_cmd_delay=options.debug_cmd_delay, debug_discard_rate=options.debug_discard_rate,
              verbosity=verbosity)

if __name__ == "__main__":
    main()
