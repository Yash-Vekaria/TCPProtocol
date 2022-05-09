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


    if int(seq) == int(pointer[0]):
        # This condition will be true only when inclusion of current seq being received makes all sequences uptil highest_cumulative_sequence as received 
        if highest_cumulative_sequence + 1 == pointer[1]:
            print("Sending Acknowledgement #", highest_cumulative_sequence)
            sock.sendto(highest_cumulative_sequence.encode(), sender_address)
        else:
            print("Sending Acknowledgement #", seq)
            sock.sendto(seq.encode(), sender_address)

    else:
        # Else handles the case when a packet is lost. 
        # In such case, the sequence number of last continuous packet received is sent
        print("Sending Acknowledgement #", pointer[0] - 1)
        sock.sendto(str(pointer[0] - 1).encode(), sender_address)
        # Checks if current sequence number is higher than the highest sequence number already receives? Updates if it is
        if seq > highest_cumulative_sequence:
            highest_cumulative_sequence = seq
    
    # Removing the received sequence number from pointer list
    if int(seq) in pointer:
        pointer.remove(int(seq))
    
    # Terminates further receiving if the RWND is reached
    if len(pointer) == 0:
        break
