# Importing the required libraries
import socket
import re


# Defining Global Parameters
# IP address of the receiver. "" implies localhost
IP_ADDRESS = ""
# Port number on localhost on which receiver runs
PORT = 5005
# Size of the buffer, defining the maximum data that can be buffered for transmission at a time
BUFFER_SIZE = 1500
# Window size at the receiver (practically very large)
RWND = 1000000


# Instatiating a UDP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Binding the Socket to specified IP address and Port
sock.bind((IP_ADDRESS, PORT))

# Implements cumulative acknowledgement by maintaining the next sequence it expects at position 0. It removes all recived sequences.
pointer = list(range(1, int(RWND)+1))
# Maintains the highest sequence number received
highest_cumulative_sequence = 1
# List containing sequence of acknowledgements that are sent to the send
sent_acknowledgements = []
# List containing sequence numbers that are unacknowledged including those that are not received)
unacknowledged_sequences = []
# List containing sequence numbers that are received by the receiver
received_sequences = []

# Receiver keeps running indefinitely to receive the data
while True:

	# Receiving the packet from the sender
	packet_data, sender_address = sock.recvfrom(BUFFER_SIZE)

	# Extracting the sequence number
	try:
		seq = re.search('Sequence Number: (.*)\r\n\r\n', packet_data.decode()).group(1)
	except AttributeError:
		seq = re.search('Sequence Number: (.*)\r\n\r\n', packet_data.decode())
	finally:
		print("Received sequence number:", seq)

	# Checking if received seq matches the next expected sequence
	if int(seq) == int(pointer[0]):

		# This condition will be true only when inclusion of current seq being received makes all sequences uptil highest_cumulative_sequence as received 
		if int(highest_cumulative_sequence) + 1 == pointer[1]:
			acknowledgement_number = int(highest_cumulative_sequence)
		else:
			# Computing sequence number within the range of highest_cumulative_sequence that are unacknowledged and unreceived
			unacknowledged_sequences = sorted(list(set(range(1, int(highest_cumulative_sequence)+1)).difference(set(sent_acknowledgements))))
            # Computing sequence number within the range of highest_cumulative_sequence that are received but unacknowledged
            temp_sequences = sorted(list(set(unacknowledged_sequences).difference(set(received_sequences))))
            
            if len(unacknowledged_sequences) != 0 and len(temp_sequences) != 0:
				if int(unacknowledged_sequences[0]) < int(highest_cumulative_sequence):
					if temp_sequences[1] - temp_sequences[0] == 1:
						acknowledgement_number = int(temp_sequences[0])
					else:
						unacknowledged_sequences.remove(int(seq))
						acknowledgement_number = int(unacknowledged_sequences[0])
			else:
				acknowledgement_number = int(seq)
	else:
		# Else handles the case when a packet is lost. In such case, the sequence number of last continuous packet received is sent
		acknowledgement_number = int(pointer[0] - 1)
		# Checks if current sequence number is higher than the highest sequence number already received? Updates if it is
		if int(seq) > int(highest_cumulative_sequence):
			highest_cumulative_sequence = seq
	
	# Sends the acknowledgement to the sender
	print("Sending Acknowledgement #", acknowledgement_number)
	sent_acknowledgements.append(int(acknowledgement_number))
	sock.sendto(str(acknowledgement_number).encode(), sender_address)
	
	# Updating the received sequences
	received_sequences.append(int(seq))

	# Removing the received sequence number from pointer list
	if int(seq) in pointer:
		pointer.remove(int(seq))
	
	# Terminates further receiving if the RWND is reached
	if len(pointer) == 0:
		break
