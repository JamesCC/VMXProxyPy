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
	@echo "    examples                     - show examples of usage"
	@echo "    test                         - unittest"
	@echo "    dist                         - create windows binaries"
	@echo "    install uninstall            - install/remove startup service for linux"
	@echo "    clean clean_test             - clean"
	@echo "    mrproper                     - clean, remove dist"
	@echo


# example run targets
examples:
	@echo
	@echo "Simulator on Network Port 10000..."
	@echo "    python3 VMXProxy -n 10000"
	@echo
	@echo "Simulator on Network Port 10000 with passcode authetication..."
	@echo "    python3 VMXProxy -n 10000 -p passcodes.txt"
	@echo
	@echo "Simulator on Serial Port /dev/ttyUSB0..."
	@echo "    python3 VMXProxy -s /dev/ttyUSB0"
	@echo
	@echo "Proxy to Serial Port /dev/ttyUSB0 on Network port 10000..."
	@echo "    python3 VMXProxy -n 10000 -s /dev/ttyUSB0"
	@echo
	@echo "Proxy to Serial Port /dev/ttyUSB0 on Network port 10000 with passcodes..."
	@echo "    python3 VMXProxy -n 10000 -s /dev/ttyUSB0 -p passcodes.txt"
	@echo


###############################################################################
# systemd install (linux)
# SN_SUFFIX can be used to create multiple VMXProxy services (with different options)
install:
	@test "$(USER)" = "root" || (echo "Please run as root or using sudo" && false)
	@test -n "$(OPTIONS)" || (echo "Please supply OPTIONS variable" && false)
	(! systemctl -q is-active VMXProxy$(SN_SUFFIX).service) || systemctl stop VMXProxy$(SN_SUFFIX).service
	perl startup_scripts/gen_service.pl $(OPTIONS) > /etc/systemd/system/VMXProxy$(SN_SUFFIX).service
	@echo
	@echo "type...  sudo systemctl start VMXProxy$(SN_SUFFIX).service      to start service now"
	@echo "         sudo systemctl status VMXProxy$(SN_SUFFIX).service     to see the status"
	@echo "         journalctl -u VMXProxy$(SN_SUFFIX).service             to see the service log"
	@echo
	@echo "         sudo systemctl enable VMXProxy$(SN_SUFFIX).service     to start service automatically at bootup"
	@echo "         sudo systemctl stop VMXProxy$(SN_SUFFIX).service       to stop service"
	@echo "         sudo systemctl disable VMXProxy$(SN_SUFFIX).service    to disable service starting at bootup"

uninstall:
	@test "$(USER)" = "root" || (echo "Please run as root or using sudo" && false)
	@test -f /etc/systemd/system/VMXProxy$(SN_SUFFIX).service || (echo "VMXProxy$(SN_SUFFIX).service is not installed" && false)
	(! systemctl -q is-active VMXProxy$(SN_SUFFIX).service) || systemctl stop VMXProxy$(SN_SUFFIX).service
	systemctl disable VMXProxy$(SN_SUFFIX).service
	rm -f /etc/systemd/system/VMXProxy$(SN_SUFFIX).service

###############################################################################
# (fallback) traditional systemV init.d install (linux)
install_initd:
	@test "$(USER)" = "root" || (echo "Please run as root or using sudo" && false)
	@test -n "$(OPTIONS)" || (echo "Please supply OPTIONS variable" && false)
	perl startup_scripts/gen_initrc.pl $(OPTIONS) > /etc/init.d/VMXProxyStartup
	chmod 755 /etc/init.d/VMXProxyStartup
	update-rc.d VMXProxyStartup defaults
	@echo "type...  /etc/init.d/VMXProxyStartup start  to start service now."

uninstall_initd:
	@test "$(USER)" = "root" || (echo "Please run as root or using sudo" && false)
	@echo "The following command will error if VMXProxyStart is not installed (ignore it)."
	/etc/init.d/VMXProxyStartup stop
	update-rc.d -f  VMXProxyStartup remove


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
