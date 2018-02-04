#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A Unit test module for VMXProcessor.

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
__license__ = "LGPLv3"

import unittest
from VMXProcessor import VMXProcessor

class TestVMXProcessor(unittest.TestCase):
    """Unittests for VMXProcessor."""

    def test_vrc_vrq(self):
        """Test we can process a global (non input channel specific) command and get the correct
        responses."""
        vmxsim = VMXProcessor()
        output = vmxsim.process(chr(2)+"VRC:1.010,1.010,1.010;")
        self.assertEqual(output, chr(6))
        output = vmxsim.process(chr(2)+"VRQ;")
        self.assertEqual(output, chr(2)+"VRS:1.010,1.010,1.010;")

    def test_ptc_ptq(self):
        """Test we can process an input channel specific command and get the correct responses."""
        vmxsim = VMXProcessor()
        output = vmxsim.process(chr(2)+"PTC:I1,1;")
        self.assertEqual(output, chr(6))
        output = vmxsim.process(chr(2)+"PTQ:I1;")
        self.assertEqual(output, chr(2)+"PTS:I1,1;")
