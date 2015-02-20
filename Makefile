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

all: test

# run targets
nsim:
	python2 vmxproxypy/VMXProxy.py -v -n 10000

ssim:
	python2 vmxproxypy/VMXProxy.py -v -s /dev/ttyUSB0

proxy:
	python2 vmxproxypy/VMXProxy.py -n 10000 -s /dev/ttyUSB0

###############################################################################
# backup
dropboxBackup:
	tar -C .. -cjf ~/Dropbox/Projects/VMXProxyPy/VMXProxyPy.tgz VMXProxyPy
	ls -l ~/Dropbox/Projects/VMXProxyPy/
	tar -tjf ~/Dropbox/Projects/VMXProxyPy/VMXProxyPy.tgz


###############################################################################
# lint
lint:
	pylint --rcfile=pylint.rcfile -f parseable vmxproxypy | tee pylint.out


###############################################################################
# test
test:
	nosetests -v --with-xunit --all-modules --traverse-namespace --with-coverage --cover-package=vmxproxypy --cover-inclusive
	python2 -m coverage xml --include="vmxproxypy/*"
	# outputs coverage.xml, nosetest.xml

testcoverageHTML: test
	coverage html
	google-chrome htmlcov/index.html &

# legacy test run method
testUNIT: clean_test 
	coverage run -m unittest discover vmxproxypy/test
	coverage xml

# legacy TAP output test run method
testTAP: clean_test
	coverage run python2 vmxproxypy/test/tapout.py
	coverage xml
	prove -e cat test-reports/*.tap

# legacy XML/JUNIT output test run method
testXML testJUNIT: clean_test
	coverage run python2 vmxproxypy/test/xmlout.py
	coverage xml


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

