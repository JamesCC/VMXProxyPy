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
import unittest
import re
import time
import socket
import os, signal
from multiprocessing import Process

from vmxproxypy import VMXProxy

STX = chr(2)
ACK = chr(6)

@unittest.skip("Does not work with coverage module")
class TestVMXProxy(unittest.TestCase):
    """Unittests for VMXProxy Application"""

    def testAsClientNoPass(self):
        """Check VMXProxy accepts a client without a password."""

        # setup VMXProxy configuration (as not using command line)
        VMXProxy.PORT = 10000
        VMXProxy.SERIAL = None
        VMXProxy.PASSWORD = None

        p = Process(target=VMXProxy.main)
        p.start()
        time.sleep(1)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("localhost", 10000))
            s.settimeout(3)

            # send some commands an check the responses
            s.send(STX+"VRQ;")
            self.assertEqual(s.recv(1024), STX+"VRS:1.010,1.010,1.010;")
            s.send("junk")
            s.send(STX+"MUC:I1,1;")
            self.assertEqual(s.recv(1024), ACK)
            s.send(STX+"MUF:I1,1;")
            self.assertEqual(s.recv(1024), STX+"ERR:0;")

        finally:
            s.close()
            os.kill(p.pid, signal.SIGINT)
            p.join()

    def testAsClientWithPass(self):
        """Check VMXProxy accepts a client with a password, and it has to be
        correct."""

        # setup VMXProxy configuration (as not using command line)
        VMXProxy.PORT = 10000
        VMXProxy.SERIAL = None
        VMXProxy.PASSWORD = "Pa$$worD"

        p = Process(target=VMXProxy.main)
        p.start()
        time.sleep(1)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("localhost", 10000))
            s.settimeout(3)

            # send incorrect password
            s.send(STX+"###PWD:Password;")
            self.assertEqual(s.recv(1024), STX+"ERR:6;")

            # send correct password
            s.send(STX+"###PWD:Pa$$worD;")
            self.assertEqual(s.recv(1024), ACK)

            # send some commands an check the responses
            s.send(STX+"VRQ;")
            self.assertEqual(s.recv(1024), STX+"VRS:1.010,1.010,1.010;")
            s.send("junk")
            s.send(STX+"MUC:I1,1;")
            self.assertEqual(s.recv(1024), ACK)

        finally:
            s.close()
            os.kill(p.pid, signal.SIGINT)
            p.join()

    def testAsTwoClients(self):
        """Check VMXProxy can accept multiple clients."""

        # setup VMXProxy configuration (as not using command line)
        VMXProxy.PORT = 10000
        VMXProxy.SERIAL = None
        VMXProxy.PASSWORD = None

        p = Process(target=VMXProxy.main)
        p.start()
        time.sleep(1)

        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s1.connect(("localhost", 10000))
            s1.settimeout(3)
            s1.send(STX+"VRQ;")
            s2.connect(("localhost", 10000))
            s2.settimeout(3)

            # send simple command
            self.assertEqual(s1.recv(1024), STX+"VRS:1.010,1.010,1.010;")

            # interleave two commands
            s1.send(STX+"MUC:I")
            s2.send(STX+"PTC:I1,1;")
            self.assertEqual(s2.recv(1024), ACK)
            s1.send("1,0;")
            self.assertEqual(s1.recv(1024), ACK)

            # check the commands executed correctly
            s1.send(STX+"MUQ:I1;")
            self.assertEqual(s1.recv(1024), STX+"MUS:I1,0;")
            s2.send(STX+"PTQ:I1;")
            self.assertEqual(s2.recv(1024), STX+"PTS:I1,1;")

        finally:
            s2.close()
            s1.close()
            os.kill(p.pid, signal.SIGINT)
            p.join()
