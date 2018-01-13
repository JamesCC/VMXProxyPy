#!/bin/bash

cd $(dirname $BASH_SOURCE)
if [ -x "$(command -v python3)" ]; then
    python3 VMXProxy "$@"
else
    python VMXProxy "$@"
fi

echo
read -rsp $'Press any key to continue...\n' -n1 key
