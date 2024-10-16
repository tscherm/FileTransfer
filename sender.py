import argparse
import socket
from datetime import datetime, timedelta
import os
import ctypes
import sys

# set up arg
parser = argparse.ArgumentParser(description="Send part of a file in packets to a reciever")

parser.add_argument("-p", "--sender_port", type=int, required=True, dest="sPort")
parser.add_argument("-g", "--requester_port", type=int, required=True, dest="rPort")
parser.add_argument("-r", "--rate", type=int, required=True, dest="rate")
parser.add_argument("-q", "--seq_no", type=int, required=True, dest="seqNo")
parser.add_argument("-l", "--length", type=int, required=True, dest="length")

args = parser.parse_args()

# milliseconds per packet
mspp = timedelta(seconds = (1 / args.rate))

# file to send
toSendName = "split.txt"
toSend = open(toSendName, "r")
toSendSize = os.stat(toSendName).st_size

# open port (to listen on only?)
hostname = socket.gethostname()
ipAddr = socket.gethostbyname(hostname)

reqAddr = (ipAddr, args.sPort)

recSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recSoc.bind(reqAddr)

# socket to send from (not the same one)
sendSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def printPacket(ptype, time, destAddr, seqNo, length, payload):
    print(f"{ptype} Packet")
    timeStr = (time.strftime("%y-%m-%d %H:%M:%S.%f"))[:-3]
    print(f"send time:\t{timeStr}")
    print(f"requester addr:\t{destAddr}:{args.rPort}")
    print(f"Sequence num:\t{seqNo}")
    print(f"length:\t\t{ctypes.c_uint32(length).value}")
    print(f"payload:\t{payload[0:4].decode('utf-8')}\n")

# send packet with respect to time
def sendPacketTimed(packet, addr, lastTimeSent):
    # wait for time to be ready to send 
    while ((datetime.now() - lastTimeSent) < mspp):
        continue

    toReturn = datetime.now()
    sendSoc.sendto(packet, (addr, args.rPort))

    return toReturn

# handle request packet
def handleReq(data, addr):
    print(f"REQUEST RECIEVED: {data}")
    # check that it is a request packet
    # 'R' = 82
    if (data[0] != 82):
        return -1
    
    print(f"PROCESSING STARTED")
    # get the number of packets to send
    numPackets = toSendSize // ctypes.c_uint32(args.length).value if toSendSize % ctypes.c_uint32(args.length).value == 0 else toSendSize // ctypes.c_uint32(args.length).value + 1

    # iterate over chunks of data and send it
    lastTime = datetime.now() - timedelta(days=1)
    seqNum = args.seqNo
    sizeLeft = toSendSize
    for i in range(numPackets):
        # make header
        pSize = ctypes.c_uint32(args.length).value if sizeLeft >= ctypes.c_uint32(args.length).value else sizeLeft
        header = b'D' + socket.htonl(seqNum).to_bytes(4, 'big') + socket.htonl(pSize).to_bytes(4, 'big')

        # get payload and add header to packet
        payload = toSend.read(pSize).encode('utf-8')
        packet = header + payload

        lastTime = sendPacketTimed(packet, addr, lastTime)

        # print packet info
        printPacket("DATA", lastTime, addr, seqNum, pSize, payload)
        seqNum += pSize

    # send END packet
    pt = b'R'
    l = 0

    packet = pt + socket.htonl(seqNum).to_bytes(4, 'big') + socket.htonl(l).to_bytes(4, 'big')
    sendPacketTimed(packet, addr, lastTime)
    


# fucntion to listen for packets and send packets elsewhere
def waitListen():
    # only need to listen and get one request
    data, addr = recSoc.recvfrom(2048)
    handleReq(data, addr[0])


def cleanup():
    toSend.close()
    recSoc.close()
    sys.exit()

def main():
    print("STARTED SENDER")
    waitListen()
    cleanup()


if __name__ == '__main__':
    main()
