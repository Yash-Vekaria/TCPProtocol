#!/bin/bash

# setting interface configuration for the locahost traffic: maximum transmission unit = 1500 bytes
sudo ifconfig lo mtu 1500

# setting the TCP/IP congestion control algorithm: default = Reno, Recommended = Cubic
sudo sysctl -w net.ipv4.tcp_congestion_control=cubic
#sudo tc qdisc add dev lo parent 1:1 handle 10: netem loss 10%

# configuring traffic controller (tc) to add a new queuing discipline (qdisc) (it actually replaces the default): tbf to localhost (lo) interface with given rate.
# tbf (token bucket filter): Outgoing (egress) traffic bytes is serviced by a single token. These tokens are stored in a bucket of limited size and refreshed at the desired output rate.
# transmit the bursts at a peakrate (rate at which buffer empties) of 1001kbit and minimum burst (buffer) of 1550 bytes to be sent at maximum rate, so a typical packet can be sent at once (MTU = 1500).
# ref: https://man7.org/linux/man-pages/man8/tc-tbf.8.html
sudo tc qdisc add dev lo root handle 1: tbf rate 1000kbit buffer 10000000 limit 500000000 peakrate 1001kbit minburst 1550

#sudo tc qdisc add dev lo parent 1:1 handle 10: netem loss 10%

# delay packets from a uniform distribution with 100ms +- 10ms (i.e., 90ms-110ms) using netem (network emulation)
sudo tc qdisc add dev lo netem loss 0.5%
sudo tc qdisc add dev lo parent 1:1 handle 10: netem loss 0.5% delay 100ms 10ms

echo "entering loop"
while :
do
	echo "200kbps for 5 seconds"
	sudo tc qdisc change dev lo root tbf rate 500kbit buffer 10000000 limit 500000000 peakrate 501kbit minburst 1550
	sleep 5
	echo "600kbps for 5 seconds"
	sudo tc qdisc change dev lo root tbf rate 1000kbit buffer 10000000 limit 500000000 peakrate 1001kbit minburst 1550
	sleep 5
	echo "900kbps for 15 seconds"
	sudo tc qdisc change dev lo root tbf rate 1000kbit buffer 10000000 limit 500000000 peakrate 1001kbit minburst 1550
	sleep 15
	echo "500kbps for 5 seconds"
	sudo tc qdisc change dev lo root tbf rate 700kbit buffer 10000000 limit 500000000 peakrate 701kbit minburst 1550
	sleep 5
done
