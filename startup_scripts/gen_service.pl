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
[Unit]
Description=VMXProxy Daemon
After=default.target

[Service]
ExecStart=/bin/bash __INSTALL_DIR__/start_VMXProxy.sh __ARGS__
Type=simple
User=__USER__
Restart=always
RestartSec=10
StartLimitInterval=300
StartLimitBurst=5

[Install]
WantedBy=default.target
