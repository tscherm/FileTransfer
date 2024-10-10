import argparse
import socket
from datetime import datetime, timedelta


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

# open port (to listen on only?)
hostname = socket.gethostname()
ipAddr = socket.gethostbyname(hostname)

reqAddr = (ipAddr, args.port)

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
    sendSoc.sendto(packet, addr)

# handle request packet
def handleReq(data, addr):
    if (data[:1][0] != 'R'):
        return -1
    
    #int numPackets = 

    #for(int )


# fucntion to listen for packets and send packets elsewhere
def waitListen():
    while isListening:
        data, addr = recSoc.recvfrom(1024)



def main():
    print("STARTED")

if __name__ == '__main__':
    main()
