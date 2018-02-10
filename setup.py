#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup file for creating a binary distribution."""

import os
import glob
from cx_Freeze import setup, Executable
from VMXProxy.__init__ import __version__

PYTHONBASE = os.path.dirname(os.path.dirname(os.__file__))

os.environ['TCL_LIBRARY'] = PYTHONBASE+'/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = PYTHONBASE+'/tcl/tk8.6'

RESOURCES = ["COPYING", "COPYING.lesser", "readme.md"] \
            + ["simrc.txt", "passcodes.txt"] + glob.glob("*.bat")

BUILD_EXE_OPTIONS = {"packages": ["VMXProxy"],
                     "add_to_path": False,
                     "include_files" : [PYTHONBASE+'/DLLs/tcl86t.dll',
                                        PYTHONBASE+'/DLLs/tk86t.dll'] + RESOURCES}

# compress packages to save space
BUILD_EXE_OPTIONS.update({"zip_include_packages": "*", "zip_exclude_packages": ""})

setup(
    name='VMXProxy',
    version=__version__,
    description='An optimised network bridge for accessing Roland V Mixer desks',
    author='James Covey-Crump',
    license='Lesser GPLv3',
    options={"build_exe": BUILD_EXE_OPTIONS},
    executables=[Executable("start_VMXProxy.py",
                            shortcutName="VMX Proxy", shortcutDir="DesktopFolder")])
