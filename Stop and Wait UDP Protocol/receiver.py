import socket
import select
import time
import random


UDP_IP = ""
IN_PORT = 5005
timeout = 1
count = 0
sleep_t = (timeout * 2 ** count + random.uniform(0, 1))

buf=1000
tar_size = 3000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((UDP_IP, IN_PORT))

data = "ping"
sock.sendto(data.encode('ascii'), (UDP_IP, IN_PORT))

data, addr = sock.recvfrom(buf)
# file_name = data.strip()
# print ("File name:", file_name)
n_packet = data.decode()
print("num of packet to receive",n_packet)

f = open("test.txt", 'wb')

received = []

check = list(range(1,int(n_packet)+1))
print("check list",check)
while True:
    t1 = time.perf_counter_ns()

    data, addr = sock.recvfrom(buf)
    f.write(data)
    seq = data.decode()[0]
    print("size of data received:",len(data))

    t2 = time.perf_counter_ns()
    time_delta = t2 - t1

    if data == b'END':
        print ("Received ", received)
        break

    else:
        print("received sequence number",seq)
        print("send acknowledgement seq %s to server:" %seq)
        x = random.randrange(1,5)
        print("x",x)
        if x>=2:
            sock.sendto(seq.encode('ascii'), (UDP_IP, IN_PORT))
            received.append(seq)
            print("received",received)
            if int(seq) in check:
                check.remove(int(seq))
            print("check list", check)

        else:
            time.sleep(2)
            print("no acknowledgement sent")



print ("File Downloaded")
