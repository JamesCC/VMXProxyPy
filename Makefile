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

.PHONY: all help examples
.PHONY: install_proxy install_sim install_status uninstall
.PHONY: dist
.PHONY: test
.PHONY: clean_test clean mrproper

all: help

help:
	@echo
	@echo "Make targets:"
	@echo "    examples                     - example usage"
	@echo "    test                         - unittest"
	@echo "    dist                         - create windows binaries"
	@echo "    clean clean_test             - clean"
	@echo "    mrproper                     - clean, remove dist"
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
	@echo "Proxy to Serial Port /dev/ttyUSB0 on Network port 10000 with passcodes..."
	@echo "    python VMXProxy -n 10000 -s /dev/ttyUSB0 -p passcodes.txt"
	@echo


###############################################################################
# install (linux)
install:
ifeq ($(USER),root)
	perl startup_scripts/gen_initrc.pl $(OPTIONS) > /etc/init.d/VMXProxyStartup
	chmod 755 /etc/init.d/VMXProxyStartup
	update-rc.d VMXProxyStartup defaults
	@echo "type...  /etc/init.d/VMXProxyStartup start  to start service now."
else
	@echo Please run as root or using sudo
endif

install_status:
ifeq ($(USER),root)
	/etc/init.d/VMXProxyStartup status
else
	@echo Please run as root or using sudo
endif

uninstall:
ifeq ($(USER),root)
	@echo "The following command will error if VMXProxyStart is not installed (ignore it)."
	/etc/init.d/VMXProxyStartup stop
	update-rc.d -f  VMXProxyStartup remove
else
	@echo Please run as root or using sudo
endif


###############################################################################
# cx_freeze
dist:
	python setup.py bdist_msi


###############################################################################
# test
test: clean_test
	coverage run -m unittest discover VMXProxy
	coverage html
	coverage report
	echo "Coverage results in htmlcov/index.html"


###############################################################################
# clean
clean_test:
	coverage erase
	-rm -rf htmlcov
	-rm -rf test-reports
	-rm -f coverage.xml

clean: clean_test
	-rm -f VMXProxy/*.pyc test/*.pyc
	-rm -rf VMXProxy/__pycache__ test/__pycache__
	-rm -rf build

mrproper: clean
	-rm -rf dist
