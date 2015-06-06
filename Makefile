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
	@echo "    mrproper                     - clean, remove dist32 dist64"
	@echo "    install uninstall            - install/remove startup service for linux"
	@echo


# example run targets
examples:
	@echo
	@echo "Simulator on Network Port 10000..."
	@echo "    python VMXProxy -n 10000"
	@echo
	@echo "Simulator on Network Port 10000 with passcode authetication..."
	@echo "    python VMXProxy -n 10000 -p passcodes.txt"
	@echo
	@echo "Simulator on Serial Port /dev/ttyUSB0..."
	@echo "    python VMXProxy -s /dev/ttyUSB0"
	@echo
	@echo "Proxy to Serial Port /dev/ttyUSB0 on Network port 10000..."
	@echo "    python VMXProxy -n 10000 -s /dev/ttyUSB0"
	@echo


###############################################################################
# install (linux)
install:
	sed "s%__INSTALL_DIR__%${PWD}%" VMXProxy.initrc > /etc/init.d/VMXProxyStartup
	chmod 755 /etc/init.d/VMXProxyStartup
	update-rc.d VMXProxyStartup defaults
	@echo "type...  sudo /etc/init.d/VMXProxyStartup start to start service now."

uninstall:
	@echo "You need to run as root for these commands to work (sudo make uninstall)"
	@echo "The following command will error if VMXProxyStart is not installed (ignore it)."
	/etc/init.d/VMXProxyStartup stop
	update-rc.d -f  VMXProxyStartup remove


###############################################################################
# lint
lint:
	pylint --rcfile=pylint.rcfile -f parseable VMXProxy --ignore=pybonjour.py,test | tee pylint.out


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
	coverage run -m unittest discover VMXProxy/test
	coverage html
	coverage report
	echo "Coverage results in htmlcov/index.html"

# legacy TAP output test run method
testTAP: clean_test
	coverage run VMXProxy/test/tapout.py
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
	-rm -f VMXProxy/*.pyc VMXProxy/test/*.pyc
	-rm -rf build

mrproper: clean
	-rm -rf dist32 dist64
