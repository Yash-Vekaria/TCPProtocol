#!/bin/bash
# setting interface configuration for the locahost traffic: maximum transmission unit = 1500 bytes
sudo ifconfig lo mtu 1500
# setting the TCP/IP congestion control algorithm: default = Reno, Recommended = Cubic
sudo sysctl -w net.ipv4.tcp_congestion_control=cubic
# configuring traffic controller (tc) to add a new queuing discipline (qdisc) (it actually replaces the default) to localhost (lo) interface with tbf rate.
# tbf (token bucket filter): Outgoing (egress) traffic bytes is serviced by a single token. These tokens are stored in a bucket of limited size and refreshed at the desired output rate.
sudo tc qdisc add dev lo root handle 1: tbf rate 1000kbit buffer 
