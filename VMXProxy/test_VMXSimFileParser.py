#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A Unit test module for VMXSimFileParser.

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
__cpyright__ = "Copyright 2018, James Covey-Crump"
__license__ = "GPLv3"

import os
import unittest
from VMXSimFileParser import VMXSimFileParser

TESTDIR = os.path.dirname(os.path.realpath(__file__))

class MockCommandProcessor:
    """Mock command processor to respond ACK to all issued commands."""
    def process(self, string):
        """Simpy return ack to everything asked to process."""
        return chr(6)

class TestVMXSimFileParser(unittest.TestCase):
    """Unittests for VMXSimFileParser"""

    def test_parser(self):
        """Test reading of simulation initialisation file for issuing commands."""
        sfp = VMXSimFileParser(MockCommandProcessor())
        successful_commands, commands = sfp.read_file(TESTDIR+"/test_VMXSimFileParser-parser.txt")
        self.assertEqual(successful_commands, 575)
        self.assertEqual(commands, 577)
