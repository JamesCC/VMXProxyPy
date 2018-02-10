import os
import glob
from cx_Freeze import setup, Executable
from VMXProxy.__init__ import __version__

PYTHONBASE = os.path.dirname(os.path.dirname(os.__file__))

os.environ['TCL_LIBRARY'] = PYTHONBASE+'/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = PYTHONBASE+'/tcl/tk8.6'

resources = ["COPYING", "COPYING.lesser", "readme.md"] \
            + ["simrc.txt", "passcodes.txt"] + glob.glob("*.bat")

build_exe_options = {"packages": ["VMXProxy"],
                     "include_files" : [PYTHONBASE+'/DLLs/tcl86t.dll', 
                                        PYTHONBASE+'/DLLs/tk86t.dll'] + resources}

# compress packages to save space
build_exe_options.update({"zip_include_packages": "*", "zip_exclude_packages": ""});

setup(
    name = 'VMXProxy',
    version = __version__,
    description = 'An optimised network bridge for accessing Roland V Mixer desks',
    author = 'James Covey-Crump',
    license = 'Lesser GPLv3',
    options = {"build_exe": build_exe_options},
    executables = [Executable("start_VMXProxy.py")])
