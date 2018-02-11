#!/usr/bin/env perl

die "Please supply OPTIONS" unless scalar(@ARGV);

while(<DATA>)
{
    s/__USER__/$ENV{'SUDO_USER'}/;
    s/__INSTALL_DIR__/$ENV{'PWD'}/;
    s/__ARGS__/@ARGV/;
    print;
}

__DATA__
#! /bin/sh
# /etc/init.d/VMXProxyStartup 

### BEGIN INIT INFO
# Provides:          VMXProxy
# Required-Start:    $remote_fs $syslog
# Should-Start:      avahi
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Simple script to start VMXProxy at boot
# Description:       A simple script that will start / stop VMXPorxy at boot / shutdown.
### END INIT INFO

# If you want a command to always run, put it here
if [ $(id -u) = 0 ]; then
   RUNUSER="runuser -u __USER__ --"
else
   RUNUSER=""
fi

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting VMXProxy"
    echo "Supplied options: __ARGS__"
    pkill -f VMXProxy.py && echo "Stopped existing VMXProxy"
    $RUNUSER __INSTALL_DIR__/start_VMXProxy.sh __ARGS__ 2>&1 | logger -t VMXProxy.py &
    ;;

  stop)
    pkill -f VMXProxy.py && echo "Stopped VMXProxy"
    ;;

  restart)
    $0 stop
    $0 start
    ;;

  status)
    pgrep -fa start_VMXProxy.py && (grep VMXProxy.py /var/log/messages | tail)
    ;;

  *)
    echo "Usage: /etc/init.d/VMXProxyStartup {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0

