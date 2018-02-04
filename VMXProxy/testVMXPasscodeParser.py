#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A Unit test module for VMXPasscodeParser.

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

import unittest
from VMXPasscodeParser import VMXPasscodeParser

class TestVMXPasscodeParser(unittest.TestCase):
    """Unittests for VMXPasscodeParser."""

    def test_parser(self):
        """Test passcode parser correctly parses a passcode file and identifies the rights."""
        acp = VMXPasscodeParser()
        acp.read_file("VMXProxy/testVMXPasscodeParser-passcodes.txt")

        self.assertEqual(acp.get_access_rights("0123"), "*M1234567890123456")
        self.assertEqual(acp.get_access_rights("10"), "------------------")
        self.assertEqual(acp.get_access_rights("912"), "")
        self.assertEqual(acp.get_access_rights("913"), "")
        self.assertEqual(acp.get_access_rights("99999"), "*-1234567890123456")
        self.assertEqual(acp.get_access_rights("2335"), "--1234567890123456")
        assert not acp.get_access_rights("8888")
        self.assertEqual(acp.get_access_rights("2345"), "*M1------8--------")
        assert not acp.get_access_rights("666")

    def test_parser_no_file(self):
        """Test passcode parser handles a missing passcode file."""
        acp = VMXPasscodeParser()
        acp.read_file("VMXProxy/test/missingfile")
        self.assertEqual(acp.get_access_rights("0123"), "")
