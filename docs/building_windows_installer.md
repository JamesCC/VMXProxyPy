# Creating the Windows installer

First clean up any previous builds:

    rmdir /s build dist

You can create the installer by typing:

    python setup.py bdist_msi

You will need to have cx_freeze installed on your system.  For a completely fresh build remove
the build and dist directory prior to running that command.


---
JamesCC @ 01feb2019