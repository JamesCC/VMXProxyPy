from distutils.core import setup
import py2exe
import sys

exec(compile(open('VMXProxy/version.py').read(), 'VMXProxy/version.py', 'exec'))

sys.path.append("./VMXProxy")
setup(
    name = 'VMXProxy',
    version = __version__,
    description = 'An optimised network bridge for accessing Roland V Mixer desks',
    author = 'James Covey-Crump',
    license = 'Lesser GPLv3',
    console=['VMXProxy/VMXProxy.py'],
    options={
                "py2exe":{
                        "ignores": ['FCNTL', 'System', 'System.IO.Ports', 'TERMIOS', 'clr'],
                }
        }
    )
