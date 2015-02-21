#! /usr/bin/env python

"""A simple blocking serial port interface for the VMixer Serial protocol."""

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

import serial

class VMXSerialPort:
    """An instance of pyserial's Serial class.  It is specific to the VMixer
    Serial Protocol which will respond to every command sent.  This means we
    can send a command block awaiting for a reply.  A semicolon or ACK (0x06)
    indicated the end of a reply.  The blocking call is configurable with a
    timeout."""

    def __init__(self, device, baudrate):
        self.__serial = serial.Serial(device, baudrate, timeout=3)

    def __del__(self):
        self.__serial.close()

    def reset(self):
        """Flushes the input and output buffers of the serial port."""
        self.__serial.flushInput()
        self.__serial.flushOutput()

    def process(self, string = None):
        """Write a string to the output, and wait for a reply.  Can be called
        with no parameters just to wait for a reply."""
        if string is not None:
            self.__serial.flushInput()
            self.__serial.write(string)
        response = ""
        inside_quotes = False
        while True:
            char = self.__serial.read(1)
            response += char
            if ( char == "" or char == chr(6) ):
                break
            if ( char == "\"" ):
                inside_quotes = not inside_quotes
            if ( char == ";" and not inside_quotes ):
                break
        return response

