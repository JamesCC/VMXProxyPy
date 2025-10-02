# Development of VMXProxyPy

This file describes the key elements of how to setup VS Code to develop
VMXProxyPy using WSL2 and docker with a Windows Host.

WSL2 is used to provide a familiar Linux (UNIX) environment for code inspection,
modification, execution.

Docker is used to containerise that environment so that WSL2 remains untouched
by installed tools and applications required for this development.  It also
makes sure we know exactly what is needed to build and run this software.


# Installing WSL2

Open a Windows PowerShell as administrator and run:

    wsl --install -d Ubuntu-24.04


# Installing Docker under WSL2

We use Linux docker rather the docker Desktop, as that is better known and
easier to script (and without complex licence arrangements).

You can get the latest docker by:

    curl -sSL get.docker.com | sh    # wait the 20s
    sudo usermod $USER -aG docker

The latter command lets you run docker as a regular user (rather than as root).

For simplicity you should then shutdown WSL2.  Exit, and in a Windows
PowerShell (still as administrator):

    wsl --shutdown

Many other guides will then take you through many steps to get docker to start
at boot.  Here at the end of 2025, I have found I didn't need to any further
steps.

To test in a PowerShell run:

    wsl -d Ubuntu-24.04

and under the resulting terminal: 

    docker run hello-world

and look for:

    Hello from Docker!
    This message shows that your installation appears to be working correctly.


# Running VS Code

Start VS Code and install the following plugins:

- WSL
- Dev Containers

You might also consider

- Git Graph - a plugin that helps visualise your git commits

Restart VS Code and when it starts from the command palette select
"WSL: Connect to WSL".

Once done, Terminal->New Terminal and git clone the repo:

    git clone https://github.com/JamesCC/VMXProxyPy.git

Create a VS Code workspace and save the corresponding
`VMXProxyPy.code-workspace` file in the root of this repository.

Open the command palette and "Reopen in Container".


## What is happening

The file `.devcontainer/devcontainer.json` is what tells VS Code to load a
container.  VS Code finds it automatically if it has that name relative to the
`VMXProxyPy.code-workspace` file.  

`devcontainer.json` references `Dockerfile` which is a standard Docker script to
build the image required (it can be used outside of VS Code).  Should you have
any new package dependencies, Python modules or system, you should add them
there.

When VS Code start the container, it will automatically mount the workspace
under `/workspaces` so your source files are still on the WSL2 system and can be
shared between containers, but importantly are not lost if the container is
rebuilt.

Note we don't use a python virtual environment here (venv) as docker is
providing the contained environment.


# Networking and Firewalls

## Port Forwarding

We want to run a server with a network interface, so we need to expose its
ports.  We do this with the following line in `.devcontainer/devcontainer.json`:

    "forwardPorts": [10000],

Forwarding 10000 to localhost (127.0.0.1) on the host (Windows, not WSL2).

This is good and secure except it some situations it would be better to if it
was all interfaces (not localhost) so you could run an App on your WiFi network
and connect to it.

Unfortunately VS Code seem to stubbornly use localhost regardless of the
"Remote: Local Port Host" setting.

We get around this by port forwarding again in Windows.  In a PowerShell (as
administrator) run:

   netsh interface portproxy add v4tov4 listenport=10000 listenaddress=0.0.0.0 connectport=10000 connectaddress=127.0.0.1

You can check for any portproxy forwarding with:

    netsh interface portproxy show v4tov4

And, at some later date, you can delete it with:

    netsh interface portproxy delete v4tov4 listenport=10000 listenaddress=0.0.0.0

This forwards any traffic on any network interface on the Windows host to
localhost:10000


## Firewall

You also need to open up the firewall.

In a PowerShell (as administrator) run:

    New-NetFirewallRule -DisplayName 'WSL2 Port 10000 Access' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 10000 -Profile Any

Or just open the Window Firewall GUI.


# Limitations

This is for simulation only.

Access to the serial port is possible by creating a pass through device, but
left to the reader to figure out.  The serial port device needs to pass through
to WSL and then to the docker container.  There a several step involved.

For using the serial port function of VMXProxyPy I would move to installing and
running the script on a device such as a Raspberry PI - it is far simpler to be
working natively.  It also helps with debugging other system related issues only
found when running on the final target.
