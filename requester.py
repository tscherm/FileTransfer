import argparse
import socket

# set up arg
parser = argparse.ArgumentParser(description="Request part of a file in packets to a reciever")

parser.add_argument("-p", "--port", type=int, required=True, dest="port")
parser.add_argument("-o", "--file_option", type=str, required=True, dest="fileName")

args = parser.parse_args()

# open port (to listen on only?)
hostname = socket.gethostname()
ipAddr = socket.gethostbyname(hostname)

reqAddr = (ipAddr, args.port)

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind(reqAddr)

def printPacket(ptype, time, srcAddr, srcPort, seq, length, percent, payload):
    print(f"{ptype} Packet")
    timeStr = (time.strftime("%y-%m-%d %H:%M:%S.%f"))[:-3]
    print(f"recieve time:\t{timeStr}")
    print(f"sender addr:\t{srcAddr}:{srcPort}")
    print(f"sequence:\t{seq}")
    print(f"length:\t{length}")
    if (ptype == "DATA"):
        print(f"percentage:\t{percent:.1%}")
    print(f"payload:\t{payload}\n")


# function to send request to specified sender
def sendReq(destIP, port):
    pt = 'R'
    seq = 0
    l = 0

    header = (pt.to_bytes(1, 'big'), seq.to_bytes(4, 'big'), l.to_bytes(4, 'big'))
    soc.sendto(header, (destIP, port))



def main():
    print("START REQUESTER")

if __name__ == '__main__':
    main()
