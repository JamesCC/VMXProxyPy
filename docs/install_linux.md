# Installing under Linux

## Basic environment

You will need root privileges, which is provided by use of the command `sudo`.

For Linux PC's running Fedora replace `apt-get` with `dnf`.
**These steps require access to the internet.**

    sudo apt-get update
    sudo apt-get install git

    python3 --version

The last command prints out the python version.  Python is very likely to already be installed on
your system.  It is recommended to use python3 where possible, although the script will work with
python 2.7 (if so, remove the 3 from `pip3` and `python3-pip` below when installing pyserial).

If you don't have python3 then install with:

    sudo apt-get install python3

VMXProxy has been tested working with python 2.7.x, and 3.5 upwards.


Now you have the environment setup, get the VMXProxy code itself...

    cd $HOME
    git clone https://github.com/JamesCC/VMXProxyPy

VMXProxy has a python module dependency on pyserial.  In most cases this will have already been
installed as part of python, but you can check (and install) by...

    sudo apt-get install python3-pip
    pip3 install pyserial

You can now run the script using...

    cd vmxproxypy
    python3 -m VMXProxy --help

You must run the script from this directory (where this readme file is), as VMXProxy expects to
find simrc.txt in the current directory.


## Installing VMXProxy as a Linux service (to run in the background)

This installs a systemd service, which can be set to run at bootup.

To install the service use `make install OPTION=...` with the OPTIONS set to the required arguments
for VMXProxy (to select which mode it runs in).   You can easily re-install to change options
at a later date if you want to experiment.


For example, to run connecting a mixer via USB serial port adaptor (usually on /dev/ttyUSB0),
without a passcode access control...

    sudo make install OPTIONS="--serial /dev/ttyUSB0 --net 10000"

OR, to run with password control **(recommended)**...

    sudo make install OPTIONS="--serial /dev/ttyUSB0 --net 10000 --passcodefile=passcodes.txt"

OR, just to try as a simulator (i.e. fake a connection to a mixer)...

    sudo make install OPTIONS="--net 10000 --passcodefile=passcodes.txt"

(see the [README.md](../README.md) for information about passcodes.txt)


To get a full list of options for VMXProxy type:

    python3 -m VMXProxy --help


After the `make install ...` commands, the service is now installed (but not yet running).


## Starting the installed VMXProxy service

> **NOTE!**  If you setup for anything other as a Simulator - remember to plug in the USB to RS232
> serial port adaptor.  You don't need to connect to the mixer yet, but not having the adaptor
> will stop the server from starting.

To start the service:

    sudo systemctl start VMXProxy.service

To monitor the status of the service:

    sudo systemctl status VMXProxy.service
    journalctl -u VMXProxy.service                  # to see the service log

To automatically start the service at boot:

    sudo systemctl enable VMXProxy.service

Replace `enable` with `stop` to stop the service and `disable` to prevent it automatically starting
at boot.


Lastly, you can remove (stop and uninstall) the service just by:

    sudo make uninstall


## Installing multiple VMXProxy services (optional)

The above will install `VMXProxy.service`.  It is possible to install several services
simulataneously by adding a suffix to the service name:

    sudo make install OPTIONS="--net 10000 --passcodefile=passcodes.txt"
    sudo make install SN_SUFFIX=-sim OPTIONS="--net 10001 --passcodefile=passcodes.txt"

Will create two services - a regular `VMXProxy.service`, and a simulator `VMXProxy-sim.service`.
Note the simulator is on port 10001, whilst the regular proxy service is on 10000.

These can then both be started and enabled to run at boot:

    sudo systemctl enable VMXProxy.service
    sudo systemctl start VMXProxy.service
    sudo systemctl enable VMXProxy-sim.service
    sudo systemctl start VMXProxy-sim.service


### Upgrading

In practice VMXProxy is fairly stable, and the only upgrades in last 3 years is the support of
Python 3, addition of a GUI for windows users, and updates on notes for installations.  There has
been no new features affecting the server itself, as the Android App manages most of the
functionality.


The following steps will upgrade your installation in place.

But first check to see if you need to upgrade.

    cd $HOME/vmxproxypy
    git status

git status will report any changes you have made to the installation.  This is likely to be
only passcodes.txt, and maybe simrc.txt.  Copy those files so you can restore the file(s)
after the upgrade.

    cp passcodes.txt $HOME

Stop the service if it is running, and uninstall it.

    make uninstall

The following will revert any changes in the vmxproxypy directory (and any subdirectories),
and pull in the latest vmxproxy.

    git reset --hard
    git pull

Then copy back any files that have changed.  It is wise to check what you are overwriting
looks similar (in case the format of the files has changed during the upgrade).

    cat passcodes.txt
    cat $HOME/passcodes.txt
    cp $HOME/passcodes.txt .

Lastly reinstall the service.  The `OPTIONS` should be options given in the `make install`
command in the previous section.

    make install OPTIONS=...

---
JamesCC @ 01feb2019