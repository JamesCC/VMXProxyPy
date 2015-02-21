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
from vmxproxypy.VMXSimFileParser import VMXSimFileParser

class mockCommandProcessor:
    def process(self, string):
        return chr(6) 

class TestVMXSimFileParser(unittest.TestCase):
    """Unittests for VMXSimFileParser"""

    def testParser(self):
        sfp = VMXSimFileParser(mockCommandProcessor())
        successfulCommands, commands = sfp.read_file("vmxproxypy/test/parser.txt")
        self.assertEqual( successfulCommands, 575 )
        self.assertEqual( commands, 577 )

