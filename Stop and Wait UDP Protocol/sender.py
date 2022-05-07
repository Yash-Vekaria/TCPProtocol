import socket
import time
import sys
import os

UDP_IP = ""
UDP_PORT = 5005
buf = 1000
file_name = "test.txt"
n_packet = 5


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', UDP_PORT))
sock.settimeout(5)

print("server is ready to send file %s" % file_name)
# f = open(file_name)
# f.seek(0, os.SEEK_END)

# sock.sendto(file_name.encode(), (UDP_IP, UDP_PORT))


# while True:
# print ("Sending %s ..." % file_name)
message, clientAddress = sock.recvfrom(buf)
print("server received:",str(message),"from",str(clientAddress))

print ("Sending Total number of packet %s ..." % str(n_packet).encode())

sock.sendto(str(n_packet).encode(), clientAddress)
check = list(range(1,int(n_packet)+1))
print("check list",check)


f = open(file_name, "r")

data = f.read(buf)

while (len(check)!=0):
    for i in check:
        l = []

        l.append(str(i))
        l.append(data)

        data = ''.join(l)
        #
        print("sending data of sequence number: ",data[0])
        print("size of the data sent:",len(data))
        # while(data):
        if(sock.sendto(data.encode(), clientAddress)):
            data = f.read(buf)
            time.sleep(0.02) # Give receiver a bit time to save

            try:
                ack, clientAddress = sock.recvfrom(buf)
                print("acknowledgement received:",int(ack),"from",str(clientAddress))
                if int(ack) in check:
                    check.remove(int(ack))
            except socket.timeout as err:
                print ('caught a timeout')
                continue


    i+=1

eof = "END"
print("check list",check)




sock.sendto(eof.encode(), clientAddress)


f.close()
sock.close()
