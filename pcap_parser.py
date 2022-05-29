import datetime
import socket
import dpkt
import math


# Global Variables

NUM_PKTS = 2409
PER_PKT_LENGTHS = [0] * (NUM_PKTS + 1)

SEND_TIMES = [0] * (NUM_PKTS + 1)
RECEIVE_TIMES = [0] * (NUM_PKTS + 1)

PER_PKT_DELAY = [0] * (NUM_PKTS + 1)
PER_PKT_THROUGHPUT = [0] * (NUM_PKTS + 1)



def compute_overall_metrics():
	"""
		Computes the Overall Performance based metrics using just timestamps of 1st and last packet
	"""
	
	global NUM_PKTS;
	global SEND_TIMES;
	global RECEIVE_TIMES;
	global PER_PKT_LENGTHS;
	global PER_PKT_DELAY;
	global PER_PKT_THROUGHPUT;

	total_delay = float(RECEIVE_TIMES[NUM_PKTS]) - float(SEND_TIMES[1])
	avg_delay = (total_delay * 1000) / (NUM_PKTS)
	avg_throughput = (sum(PER_PKT_LENGTHS) * 8) / (total_delay)
	performance_metric = math.log(avg_throughput, 10) - math.log(avg_delay, 10)

	print ("Overall Average Throughput:", avg_throughput, "bits per second")
	print ("Overall Average Delay:", avg_delay, "milliseconds")
	print ("OverallPerformance:", performance_metric)
	
	

def compute_adjusted_metrics():
	"""
		Computes the Performance based metrics by multiplying delay with 2.
		This is done to account for the time taken by acknowledgement to reach sender.
	"""
	
	global NUM_PKTS;
	global SEND_TIMES;
	global RECEIVE_TIMES;
	global PER_PKT_LENGTHS;
	global PER_PKT_DELAY;
	global PER_PKT_THROUGHPUT;

	for seq in range(1, NUM_PKTS+1):
		PER_PKT_DELAY[seq] = float(RECEIVE_TIMES[seq]) - float(SEND_TIMES[seq])
		PER_PKT_THROUGHPUT[seq] = (PER_PKT_LENGTHS[seq] * 8) / PER_PKT_DELAY[seq]

	avg_delay = (sum(PER_PKT_DELAY) / len(PER_PKT_DELAY)) * 2000
	avg_throughput = (sum(PER_PKT_THROUGHPUT) / len(PER_PKT_THROUGHPUT)) / 2
	performance_metric = math.log(avg_throughput, 10) - math.log(avg_delay, 10)

	print ("Average Throughput:", avg_throughput, "bits per second")
	print ("Average Delay:", avg_delay, "milliseconds")
	print ("Performance:", performance_metric)




def compute_metrics():
	"""
		Computes the Performance based metrics
	"""
	
	global NUM_PKTS;
	global SEND_TIMES;
	global RECEIVE_TIMES;
	global PER_PKT_LENGTHS;
	global PER_PKT_DELAY;
	global PER_PKT_THROUGHPUT;

	for seq in range(1, NUM_PKTS+1):
		PER_PKT_DELAY[seq] = float(RECEIVE_TIMES[seq]) - float(SEND_TIMES[seq])
		PER_PKT_THROUGHPUT[seq] = (PER_PKT_LENGTHS[seq] * 8) / PER_PKT_DELAY[seq]

	avg_delay = (sum(PER_PKT_DELAY) / len(PER_PKT_DELAY)) * 1000
	avg_throughput = sum(PER_PKT_THROUGHPUT) / len(PER_PKT_THROUGHPUT)
	performance_metric = math.log(avg_throughput, 10) - math.log(avg_delay, 10)

	print ("Average Throughput:", avg_throughput, "bits per second")
	print ("Average Delay:", avg_delay, "milliseconds")
	print ("Performance:", performance_metric)



def get_sequence_number(udp_data_payload):
	"""
		Extracts Seq. Number of Ack. Number from UDP Payload

		Args:
			udp_data_payload (str): UDP Data Payload
		Returns:
			str: Seq. Number (with type PSH) or Ack. Number (with type ACK)
	"""
	
	seq_number, ack_number = -1, -1
	
	if len(udp_data_payload) <= 4:
		try:
			ack_number = int(udp_data_payload)
		except:
			print("Error", udp_data_payload)
		return "ACK", ack_number
	
	elif "|" in udp_data_payload[:6]:
		seq_number = int(udp_data_payload.split("|")[0])
		return "PSH", seq_number



def get_ip_addresses(ip_object):
	"""
		Returns Source and Destination IP

		Args:
			ip_object (str): IP Object from Wireshark
		Returns:
			str: Source and Destination IP address
	"""
	
	try:
		src_ip_addr_str = inet_to_str(ip_object.src)
	except:
		src_ip_addr_str = str(ip_object.src)
	
	try:
		dst_ip_addr_str = inet_to_str(ip_object.dst)
	except:
		dst_ip_addr_str = str(ip_object.dst)

	return src_ip_addr_str, dst_ip_addr_str



# Source: https://dpkt.readthedocs.io/en/latest/_modules/examples/print_packets.html
def inet_to_str(inet):
	"""
		Convert inet object to a string

		Args:
			inet (inet struct): inet network address
		Returns:
			str: Printable/readable IP address
	"""
	
	# First try ipv4 and then ipv6
	try:
		return socket.inet_ntop(socket.AF_INET, inet)
	except ValueError:
		return socket.inet_ntop(socket.AF_INET6, inet)



def main(pcap):

	global SEND_TIMES;
	global RECEIVE_TIMES;
	global PER_PKT_LENGTHS;

	for ts, buf in pcap:
		eth = dpkt.ethernet.Ethernet(buf)
		ip = eth.data
		udp = ip.data

		protocol = ip.get_proto(ip.p).__name__
		if protocol != "UDP":
			continue

		source_ip, destination_ip = get_ip_addresses(ip)
		if source_ip != destination_ip or source_ip != "127.0.0.1":
			continue

		sequence_type, sequence_number = get_sequence_number(udp.data.decode())

		if sequence_number > 0:

			if sequence_type == "PSH":

				if PER_PKT_LENGTHS[sequence_number] == 0:
					PER_PKT_LENGTHS[sequence_number] = len(udp.data)

				if SEND_TIMES[sequence_number] == 0:
					SEND_TIMES[sequence_number] = ts

			if sequence_type == "ACK":

				for seq in range(1, sequence_number+1):

					if RECEIVE_TIMES[seq] == 0:
						RECEIVE_TIMES[seq] = ts

	# compute_metrics()
	# print()
	# compute_overall_metrics()
	print()
	compute_adjusted_metrics()


if __name__ == '__main__':

	f = open('test.pcap', 'rb')
	packets_captured = dpkt.pcap.Reader(f)
	print("\nPCAP File successfully read!\n")
	
	main(packets_captured)

