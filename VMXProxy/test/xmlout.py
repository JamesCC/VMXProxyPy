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

# pip install unittest-xml-reporting
# python2 vmxproxypy/test/xmlout.py

import os
import unittest
import logging
from xmlrunner import XMLTestRunner

os.sys.path.append('.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    tests = loader.discover(tests_dir)
    runner = XMLTestRunner(output='./test-reports')
    runner.run(tests)

