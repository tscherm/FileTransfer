import argparse
import socket
from datetime import datetime, timedelta
import os

# set up arg
parser = argparse.ArgumentParser(description="Send part of a file in packets to a reciever")

parser.add_argument("-p", "--sender_port", type=int, required=True, dest="sPort")
parser.add_argument("-g", "--requester_port", type=int, required=True, dest="rPort")
parser.add_argument("-r", "--rate", type=int, required=True, dest="rate")
parser.add_argument("-q", "--seq_no", type=int, required=True, dest="seqNo")
parser.add_argument("-l", "--length", type=int, required=True, dest="length")

args = parser.parse_args()

# milliseconds per packet
mspp = timedelta(1000000 / args.rate)

# variable to tell if port should be listening
isListening = True

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
    print(f"length:\t{length}")
    print(f"payload:\t{payload}\n")

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
    if (data[:1][0] != 'R'):
        return -1
    
    print(f"PROCESSING STARTED")
    # get the number of packets to send
    numPackets = toSendSize // args.length if toSendSize % args.length == 0 else toSendSize // args.length + 1

    # iterate over chunks of data and send it
    lastTime = datetime.now() - timedelta(year=1)
    seqNum = args.seqNo
    sizeLeft = toSendSize
    for i in range(numPackets):
        # make header
        pSize = args.length if sizeLeft >= args.length else sizeLeft
        header = b'D' + socket.htonl(seqNum).to_bytes(4) + socket.htonl(pSize).to_bytes(4)

        # get payload and add header to packet
        payload = toSend.read(pSize).encode('utf-8')
        packet = header + payload

        lastTime = sendPacketTimed(packet, addr, lastTime)

        # print packet info
        printPacket("DATA", lastTime, addr, seqNum, pSize, payload)

    # send END packet
    


# fucntion to listen for packets and send packets elsewhere
def waitListen():
    while isListening:
        data, addr = recSoc.recvfrom(2048)
        print(data)
        handleReq(data, addr[0])

def cleanup():
    toSend.close()

def main():
    print("STARTED SENDER")
    waitListen()
    cleanup()


if __name__ == '__main__':
    main()
