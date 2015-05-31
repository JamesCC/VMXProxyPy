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

all: help

help:
	@echo
	@echo "Make targets:"
	@echo "    examples                     - example usage"
	@echo "    lint                         - pylint"
	@echo "    test                         - unittest"
	@echo "    dist32 dist64                - create windows binaries"
	@echo "    clean clean_lint clean_test  - clean"
	@echo


# example run targets
examples:
	@echo
	@echo "Simulator on Network Port 10000..."
	@echo "    python vmxproxypy -n 10000"
	@echo
	@echo "Simulator on Network Port 10000 with passcode authetication..."
	@echo "    python vmxproxypy -n 10000 -p passcodes.txt"
	@echo
	@echo "Simulator on Serial Port /dev/ttyUSB0..."
	@echo "    python vmxproxypy -s /dev/ttyUSB0"
	@echo
	@echo "Proxy to Serial Port /dev/ttyUSB0 on Network port 10000..."
	@echo "    python vmxproxypy -n 10000 -s /dev/ttyUSB0"
	@echo


###############################################################################
# lint
lint:
	pylint --rcfile=pylint.rcfile -f parseable vmxproxypy --ignore=pybonjour.py,test | tee pylint.out


###############################################################################
# py2exe
dist32:
	python setup.py py2exe
	mv dist dist32

dist64:
	python setup.py py2exe
	mv dist dist64


###############################################################################
# test
test: testUNIT

# legacy test run method
testUNIT: clean_test
	coverage run -m unittest discover vmxproxypy/test
	coverage html
	coverage report
	echo "Coverage results in htmlcov/index.html"

# legacy TAP output test run method
testTAP: clean_test
	coverage run vmxproxypy/test/tapout.py
	prove -e cat test-reports/*.tap
	coverage html
	coverage report
	echo "Coverage results in htmlcov/index.html"

# clean
clean_lint:
	-rm -f pylint.out

clean_test:
	coverage erase
	-rm -rf htmlcov
	-rm -rf test-reports
	-rm -f nosetests.xml coverage.xml

clean: clean_test clean_lint
	-rm -f vmxproxypy/*.pyc vmxproxypy/test/*.pyc
	-rm -rf build
