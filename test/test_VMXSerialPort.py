#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A Unit test module for VMXSerialPort.  These tests require a loopback dongle.

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

import unittest
import time
from VMXProxy.VMXSerialPort import VMXSerialPort

SERIAL = None
#SERIAL = "/dev/ttyUSB0"


class TestVMXSerialPort(unittest.TestCase):
    """Unittests for VMXSerialPort (requires a loopback dongle)."""

    def test_simple(self):
        """Test serial port can loopback plain text."""
        if SERIAL is None:
            raise unittest.SkipTest("No Serial Port Definition")
        serial_port = VMXSerialPort(SERIAL, 115200)
        start_time = time.time()
        reply = serial_port.process("Hello;")
        delta_time = time.time() - start_time
        self.assertEqual(reply, "Hello;")
        self.assertLess(delta_time, 1)
        start_time = time.time()
        reply = serial_port.process()
        delta_time = time.time() - start_time
        self.assertEqual(reply, "")
        self.assertGreater(delta_time, 3)
        self.assertLess(delta_time, 4)

    def test_split(self):
        """Test serial port works with fragmented transmit messages."""
        if SERIAL is None:
            raise unittest.SkipTest("No Serial Port Definition")
        serial_port = VMXSerialPort(SERIAL, 115200)
        start_time = time.time()
        reply = serial_port.process("Hel")
        delta_time = time.time() - start_time
        self.assertEqual(reply, "Hel")
        self.assertGreater(delta_time, 3)
        self.assertLess(delta_time, 4)
        start_time = time.time()
        reply = serial_port.process("lo;")
        delta_time = time.time() - start_time
        self.assertEqual(reply, "lo;")
        self.assertLess(delta_time, 1)

    def test_ack(self):
        """Test serial port can handle ASCII 0x06 ack characters."""
        if SERIAL is None:
            raise unittest.SkipTest("No Serial Port Definition")
        serial_port = VMXSerialPort(SERIAL, 115200)
        start_time = time.time()
        reply = serial_port.process(chr(6))
        delta_time = time.time() - start_time
        self.assertEqual(reply, chr(6))
        self.assertLess(delta_time, 1)
