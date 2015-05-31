from distutils.core import setup
import py2exe
import sys
from vmxproxypy.VMXProxy import __version__

sys.path.append("./vmxproxypy")
setup(
    name = 'VMXProxy',
    version = __version__,
    description = 'An optimised network bridge for accessing Roland V Mixer desks',
    author = 'James Covey-Crump',
    license = 'Lesser GPLv3',
    console=['vmxproxypy/VMXProxy.py'],
    options={
                "py2exe":{
                        "ignores": ['FCNTL', 'System', 'System.IO.Ports', 'TERMIOS', 'clr'],
                }
        }
    )
