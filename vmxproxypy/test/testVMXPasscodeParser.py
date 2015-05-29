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

import sys
import unittest
import logging
from vmxproxypy.VMXPasscodeParser import VMXPasscodeParser

class TestVMXPasscodeParser(unittest.TestCase):
    """Unittests for VMXPasscodeParser"""

    def testParser(self):
    
        #ogging.basicConfig(format='%(asctime)s.%(msecs)03d:%(threadName)s:%(levelname)s - %(message)s',
        #                   datefmt='%H%M%S', level=logging.INFO)
        acp = VMXPasscodeParser()
        acp.read_file("vmxproxypy/test/passcodes.txt")

        self.assertEqual( acp.get_access_rights("0123"),  "*M1234567890123456" )
        self.assertEqual( acp.get_access_rights("10"),    "------------------" )
        self.assertEqual( acp.get_access_rights("99999"), "*-1234567890123456" )
        self.assertEqual( acp.get_access_rights("2335"),  "--1234567890123456" )
        assert not acp.get_access_rights("8888")
        self.assertEqual( acp.get_access_rights("2345"),  "*M1------8--------" )
        assert not acp.get_access_rights("666")

