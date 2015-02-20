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

import unittest
import time
from vmxproxypy.VMXSerialPort import VMXSerialPort

SERIAL = None
#SERIAL = "/dev/ttyUSB0"

class TestVMXSerialPort(unittest.TestCase):
    """Unittests for VMXSerialPort"""

    def testSimple(self):
        if SERIAL is None:
            raise unittest.SkipTest("No Serial Port Definition");
        s = VMXSerialPort(SERIAL, 115200)
        startTime = time.time()
        reply = s.process("Hello;")
        t = time.time()-startTime;
        self.assertEqual( reply, "Hello;" )
        self.assertLess( t, 1 )
        startTime = time.time()
        reply = s.process()
        t = time.time()-startTime;
        self.assertEqual( reply, "" )
        self.assertGreater( t, 3 )
        self.assertLess( t, 4 )

    def testSplit(self):
        if SERIAL is None:
            raise unittest.SkipTest("No Serial Port Definition");
        s = VMXSerialPort(SERIAL, 115200)
        startTime = time.time()
        reply = s.process("Hel")
        t = time.time()-startTime;
        self.assertEqual( reply, "Hel" )
        self.assertGreater( t, 3 )
        self.assertLess( t, 4 )
        startTime = time.time()
        reply = s.process("lo;")
        t = time.time()-startTime;
        self.assertEqual( reply, "lo;" )
        self.assertLess( t, 1 )

    def testAck(self):
        if SERIAL is None:
            raise unittest.SkipTest("No Serial Port Definition");
        s = VMXSerialPort(SERIAL, 115200)
        startTime = time.time()
        reply = s.process(chr(6))
        t = time.time()-startTime;
        self.assertEqual( reply, chr(6) )
        self.assertLess( t, 1 )


