#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A program to provide a simulator and networked proxy service for Roland's
    V-Mixer serial protocol.

    This file is part of VMXProxyPy.

    VMXProxyPy is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    VMXProxyPy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Less General Public License
    along with VMXProxyPy.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "James Covey-Crump"
__copyright__ = "Copyright 2018, James Covey-Crump"
__license__ = "LGPLv3"

import sys

import logging
import threading
import os
import time
import subprocess
import platform

if (sys.version_info > (3, 0)):
    import socketserver
else:
    # rename for benefit of python2 code
    import SocketServer as socketserver

from .VMXSimFileParser import VMXSimFileParser
from .VMXSerialPort import VMXSerialPort
from .VMXProcessor import VMXProcessor
from .VMXParser import VMXParser
from .VMXPasscodeParser import VMXPasscodeParser


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Handler container for incoming TCP connections"""

    BAD_SYNTAX_RESPONSE = chr(2) + "ERR:0;"
    NOT_AUTENTICATED_RESPONSE = chr(2) + "ERR:6;"

    def process_directive(self, command, authenticated):
        """Process special directive commands, not intended for mixer."""
        if command.startswith(chr(2) + "###PWD:"):
            if self.server.passcode_parser is None:
                logging.warning("Passcode sent, but authentication not required")
                response = chr(6)
            else:
                rights = self.server.passcode_parser.get_access_rights(command[8:-1])
                if rights:
                    response = chr(2) + "###PWD:\"" + rights + "\";"
                    logging.debug("Authenticated - " + command[7:])
                    authenticated = 1
                else:
                    logging.warning("Not Authenticated - " + command[7:])
                    response = self.NOT_AUTENTICATED_RESPONSE

        elif command.startswith(chr(2) + "###CFA"):
            # We support the Cache Feature
            logging.debug("Supporting requested caching feature")
            response = chr(6)

        else:
            response = self.BAD_SYNTAX_RESPONSE

        return response, authenticated

    # note: self.server is an instance of class ThreadedTCPServer
    #       self.request is an instance of class socket
    def handle(self):
        self.request.getsockname()
        client_ip = self.request.getpeername()[0]
        logging.info("%s Connected", client_ip)
        authenticated = (self.server.passcode_parser is None)
        command_count = 0
        tcp_input_gatherer = VMXParser()
        try:
            data = self.request.recv(1024).decode("ascii", errors="ignore")
            while data:
                command = tcp_input_gatherer.process(data)
                while command:
                    if command.startswith(chr(2) + "###"):
                        response, authenticated = self.process_directive(command, authenticated)

                    elif authenticated:
                        response = self.server.cmd_processor.process(command)
                        command_count += 1

                    else:
                        response = self.NOT_AUTENTICATED_RESPONSE

                    if response != "":
                        self.request.sendall(response.encode("ascii", errors="ignore"))
                    command = tcp_input_gatherer.process()
                data = self.request.recv(1024).decode("ascii", errors="ignore")
        except:
            pass
        logging.info("%s Disconnected (after %d commands)", client_ip, command_count)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Instance of a TCP Server that can handle multiple simultaneous
    connections."""

    def start_server(self, cmd_processor, passcode_parser=None):
        """Start the server with the supplied command processor object for handling incoming
        commands."""
        _, port = self.server_address
        logging.info("Network Server started on port %d", port)
        self.cmd_processor = cmd_processor
        self.passcode_parser = passcode_parser

        if passcode_parser is not None:
            logging.info("Authentication will be required")

        self.serve_forever()


def try_announce_service(host_port_number):
    """Attempt ZeroConf Service Announcement.  Will silently fail, in case users have not
    installed the required components in their system."""

    try:
        if platform.system() == "Windows":
            subprocess.Popen(["dns-sd", "-R", "vmxproxy", "_telnet._tcp", "local",
                              host_port_number, "vmxproxy=1"])
        elif platform.system() == "Linux":
            subprocess.Popen(["avahi-publish", "-s", "vmxproxy", "_telnet._tcp",
                              host_port_number, "vmxproxy=1"])
    except:
        pass


def vmx_proxy(serial_port_name=None, baudrate=115200,
              host_ip="", host_port_number=None, server_passcodefile=None,
              debug_cmd_delay=None, debug_discard_rate=None,
              simfilerc=os.path.abspath(os.getcwd()) + "/simrc.txt", verbosity=logging.INFO):
    """Start the vmx_proxy server / simulator"""

    logging.basicConfig(format='%(asctime)s.%(msecs)03d:%(threadName)s:%(levelname)s - %(message)s',
                        datefmt='%H%M%S', level=verbosity)

    cmd_processor = VMXProcessor()
    passcode_parser = None

    if server_passcodefile:
        passcode_parser = VMXPasscodeParser()
        passcode_parser.read_file(server_passcodefile)

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
        logging.info("Debug Mode - Delay mixer responses by up to %sms", debug_cmd_delay)
        cmd_processor.set_debug_cmd_delay_in_ms(int(debug_cmd_delay))

    if host_port_number is not None:
        # Input is from Network
        server = ThreadedTCPServer((host_ip, int(host_port_number)), ThreadedTCPRequestHandler)

        if serial_port_name is not None:
            cmd_processor.set_mixer_interface(serial_port)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.start_server,
                                         args=(cmd_processor, passcode_parser))
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        try_announce_service(host_port_number)

        try:
            while True:
                # do nothing waiting for a keyboard interrupt
                time.sleep(1)

        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
            del cmd_processor
            logging.info("Server shutdown")
            if serial_port_name is not None:
                del serial_port
                logging.info("Serial Port shutdown")

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

    else:
        logging.error("Invalid mode.  Need either or both -s or -n options.")
