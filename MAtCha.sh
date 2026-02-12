#!/bin/bash
# Bash script to change the MAC address of an adapter

if [ "$#" -ne 2 ]; then
	echo "Usage: sudo $0 <interface> <new-mac>"
	exit 1
fi

INTERFACE="$1"
NEWMAC="$2"

echo "[SPOON] Changing MAC address of $INTERFACE to $NEWMAC"

ip link set dev "$INTERFACE" down
ip link set dev "$INTERFACE" address "$NEWMAC"
ip link set dev "$INTERFACE" up


echo "[SPOON] DONE"

