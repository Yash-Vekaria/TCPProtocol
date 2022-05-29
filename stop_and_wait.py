import socket
import time
import sys
import os
import math


BUFFER_SIZE = 1000
FILENAME = "message.txt"
PKT_SIZE = 1000
NUM_PKTS = int(os.path.getsize(FILENAME)/PKT_SIZE)+1
SEND_TIME = [0]*(NUM_PKTS+1)
RECV_TIME = [0]*(NUM_PKTS+1)
SENT = [0]*(NUM_PKTS+1)
RECEIVED = [0]*(NUM_PKTS+1)
TRANSFERRED_BYTES = [0]*(NUM_PKTS+1)
ACKNOWLEDGED_SEQUENCES = [0]*(NUM_PKTS+1)
PER_PKT_RTT = [0]*(NUM_PKTS+1)
PER_PKT_THROUGHPUT = [0]*(NUM_PKTS+1)
LOST = 0

UDP_IP = ""
UDP_PORT = int(input("Enter the Port number on which your receiver is running: "))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((UDP_IP,UDP_PORT))

print("Sender is ready to send the file %s" % FILENAME)
print("Number of Packets to send:", NUM_PKTS)


def generate_plots():
	global NUM_PKTS;
	global PER_PKT_RTT;
	global PER_PKT_THROUGHPUT;
	import matplotlib.pyplot as plt
	
	packet_sequence = list(range(1, NUM_PKTS+1))

	PER_PKT_DELAY = [PER_PKT_RTT[seq]*1000 for seq in range(1, NUM_PKTS+1)]
   
	plt.plot(packet_sequence, PER_PKT_DELAY)
	plt.title('Per-packet Delays')
	plt.xlabel('Packet Sequence Numbers')
	plt.ylabel('Packet Delays')
	plt.savefig('stop_and_wait_delay.png')
	plt.show()
	
	plt.plot(packet_sequence, PER_PKT_THROUGHPUT)
	plt.title('Per-packet Throughputs')
	plt.xlabel('Packet Sequence Numbers')
	plt.ylabel('Packet Throughputs')
	plt.savefig('stop_and_wait_throughput.png')
	plt.show()



def generate_packets():
	global FILENAME;
	global BUFFER_SIZE;
	global NUM_PKTS;

	f = open(FILENAME, "r")
	message_packets = ["0"]

	for i in range(1, NUM_PKTS+1):
		file_message = f.read(BUFFER_SIZE)
		message_packets.append(file_message)

	f.close()
	return message_packets



def send_packet(seq, data, retransmission_flag):
	global SENT;
	global TRANSFERRED_BYTES;
	global SEND_TIME;

	l = []
	l.append(str(seq)+str("|"))
	l.append(data)

	data = ''.join(l)
	TRANSFERRED_BYTES[seq]=len(str.encode(data))

	if retransmission_flag == 0:
		if SEND_TIME[seq] == 0:
			SEND_TIME[seq] = time.time()

	if(sock.send(data.encode())):
		SENT[seq] = 1
		print("Sequence Number of Packet Sent: ",seq)


def receive_acknowledgement(sockt):
	global ACKNOWLEDGED_SEQUENCES;
	global PER_PKT_RTT;
	global BUFFER_SIZE;
	global LOST;

	consecutive_receive_timeouts = 3
	current_timeouts = 0

	while current_timeouts < consecutive_receive_timeouts:
		try:
			sockt.setblocking(0)
			sockt.settimeout(0.02)
			ack = sockt.recv(BUFFER_SIZE)
			ACKNOWLEDGED_SEQUENCES[int(ack)] = 1
			print("Acknowledgement Received:", int(ack))
			
			if PER_PKT_RTT[int(ack)] == 0:
				compute_metrics(int(ack))
			return
		except socket.timeout as err:
			current_timeouts += 1


def compute_metrics(ack):
	global SEND_TIME;
	global RECV_TIME;
	global PER_PKT_RTT;
	global PER_PKT_THROUGHPUT;
	global TRANSFERRED_BYTES;

	RECV_TIME[ack] = time.time()
	PER_PKT_RTT[ack] = float(RECV_TIME[ack]) - float(SEND_TIME[ack])
	PER_PKT_THROUGHPUT[ack] = (TRANSFERRED_BYTES[ack] * 8) / PER_PKT_RTT[ack]



PACKETS = generate_packets()

curr_retransmission = 0
curr_seq = 1
while curr_seq < NUM_PKTS+1:
	
	if SENT[curr_seq] == 0:
		send_packet(curr_seq, PACKETS[curr_seq], 0)
	elif curr_seq == curr_retransmission:
		send_packet(curr_seq, PACKETS[curr_seq], 1)

	while time.time() < (SEND_TIME[curr_seq] + 5):

		receive_acknowledgement(sock)
		if ACKNOWLEDGED_SEQUENCES[curr_seq] == 1:
			break
	
	if ACKNOWLEDGED_SEQUENCES[curr_seq] == 0:
		curr_retransmission = curr_seq
		LOST += 1
	else:
		curr_retransmission = 0
		curr_seq += 1


TRANSFERRED_BYTES = [(float(x)) for x in TRANSFERRED_BYTES]
PER_PKT_RTT = [(float(x)) for x in PER_PKT_RTT]
PER_PKT_THROUGHPUT= [(float(x)) for x in PER_PKT_THROUGHPUT]

AVERAGE_THROUGHPUT = sum(PER_PKT_THROUGHPUT) / len(PER_PKT_THROUGHPUT)
AVERAGE_DELAY = (sum(PER_PKT_RTT) / (len(PER_PKT_RTT)) * 1000)

print("Average Throughput:", AVERAGE_THROUGHPUT," bps (bits per second)")
print("Average Delay:", AVERAGE_DELAY," ms (milliseconds)")
print("Performance:", math.log(AVERAGE_THROUGHPUT,10) - math.log(AVERAGE_DELAY,10))
print("Packet Loss:", "Count =", LOST, "; PERCENT =", round((float(LOST)/2409)*100, 3))

generate_plots()
 
sock.close()
