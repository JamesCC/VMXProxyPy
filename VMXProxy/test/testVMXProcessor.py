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
from vmxproxypy.VMXProcessor import VMXProcessor

class TestVMXProcessor(unittest.TestCase):
    """Unittests for VMXProcessor"""

    def testVR(self):
        vmxsim = VMXProcessor();
        output = vmxsim.process(chr(2)+"VRC:1.010,1.010,1.010;")
        self.assertEqual( output, chr(6) )
        output = vmxsim.process(chr(2)+"VRQ;")
        self.assertEqual( output, chr(2)+"VRS:1.010,1.010,1.010;" )

    def testPT(self):
        vmxsim = VMXProcessor();
        output = vmxsim.process(chr(2)+"PTC:I1,1;")
        self.assertEqual( output, chr(6) )
        output = vmxsim.process(chr(2)+"PTQ:I1;")
        self.assertEqual( output, chr(2)+"PTS:I1,1;" )


