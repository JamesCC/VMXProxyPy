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

import serial

class VMXSerialPort:

    def __init__(self, device, baudrate):
        self.__serial = serial.Serial(device, baudrate, timeout=3)

    def __del__(self):
        self.__serial.close()

    def process(self, string = None):
        if string is not None:
            self.__serial.write(string)
        char = self.__serial.read(1)
        string = char
        while not ( char == "" or char == ";" or char == chr(6) ):
            char = self.__serial.read(1)
            string += char
        return string

