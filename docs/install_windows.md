# Installing on Windows

## Prebuilt Executable for Windows

For windows you don't need to install Python, you can use a prebuilt executable, distributed as a
MSI file (windows installer).  Just double click to install, and an icon will be placed on your
desktop.

The installer can be found on the website, with details of how to run it...
<https://sites.google.com/site/vmxserialremote/vmxproxy>
(to build it see [building_windows_installer.md](building_windows_installer.md))

In the installation there are additional batch files found in `startup_scripts` that can be used
to start the server without the use of the GUI.  Just double click the relevant batch file.  Edit
them if necessary to change any key settings (such as the serial port), and drop a short cut to
them on your desktop to quickly execute them.


Alternatively, you can also run the python script "normally", just install Python 3.6, download
VMXProxy from github, start a windows console, cd to the directory you create (with this readme.md
file) and type...

    python -m VMXProxy --help

Note VMXProxy has a dependency on pyserial - https://pypi.python.org/pypi/pyserial


## Automatic Discovery

If you use the "Search for Server" option in the VMX Serial Remote App, you will need to install
Apple's Bonjour (if running in Windows).  Linux systems use the equivalent called avahi.  This
allows VMXProxy to advertise its ip address and port number.

Bonjour is used in a wide variety of places, not just Apple products.  If you don't have it
installed (check Control Panel / Program and Features), the simplest method is to get it is to
install iTunes.

I fully understand if you might not want to do that.  You can install just Bonjour by itself by
downloading the itunes installer from http://www.apple.com/uk/itunes/ and using winrar or 7zip
to unpack the executable (yes you can do that).  Look for... .rsrc/RCDATA/CABINET and repeat
the unpack operation.  In there  you'll find Bonjour.msi.  Double click to install this
independently.

This has been a disappointing feature for me.  There are many reasons why this might not work
well on a network, and the solutions to get it working reliably long winded.  In practice you
may wish to stick with finding your VMXProxy's IP address and entering that.  Most router won't
change IP addresses unless they are reset.


## Upgrading

The Android App manages most of the complex functionality, and so VMXProxy is fairly stable.  There
has been no need to upgrade in last 4 years.  In 2018 Python 3 support was added, and GUI to aid
configuration for windows users, but otherwise changes are to the documentation and install scripts
keeping them up-to-date.

That said, if you want to update, just download a new copy from the website, unzip it and copy in
your passcodes.txt and simrc.txt files from your old installation before you delete it.  You may have
also altered some .bat files for starting vmxproxy.


---
JamesCC @ 01feb2019