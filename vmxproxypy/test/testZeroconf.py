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
from subprocess import check_output
from vmxproxypy.ZeroconfService import ZeroconfService

class TestZeroconf(unittest.TestCase):
    """Unittests for third party ZeroconfService"""

    def _publishAndCheck(self, ip_version_string):
        service = ZeroconfService(name="vmxproxy", port=3000, stype='_telnet._tcp', text=["vmxproxy=1"])
        service.publish()
        time.sleep(2)
        captured_output = check_output(["avahi-browse", "_telnet._tcp", "-rt"])
        logging.debug(captured_output)
        found = False
        in_details = False
        matched_port = False
        for line in captured_output.splitlines():
            if line.startswith("="):
                if line.find(ip_version_string)>=0 and line.find("vmxproxy")>=0:
                    found = True
                    in_details = True
                else:
                    in_details = False
            elif in_details and line.find("port")>=0 and line.find("3000")>=0:
                matched_port = True;
        self.assertTrue( found )
        self.assertTrue( matched_port )
        service.unpublish()

    def testZeroconfPublishIPv4(self):
        self._publishAndCheck("IPv4")

    def testZeroconfPublishIPv6(self):
        self._publishAndCheck("IPv6")

