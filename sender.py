import argparse


# set up arg
parser = argparse.ArgumentParser(description="Send part of a file in packets to a reciever")

parser.add_argument("-p", "--sender_port", type=int, required=True, dest=sPort)
parser.add_argument("-g", "--requester_port", type=int, required=True, dest=rPort)
parser.add_argument("-r", "--rate", type=int, required=True, dest=rate)
parser.add_argument("-q", "--seq_no", type=int, required=True, dest=seqNo)
parser.add_argument("-l", "--length", type=int, required=True, dest=length)

args = parser.parse_args()

def printPacket(ptype, time, destAddr, seqNo, length, payload):
    print("{ptype} Packet")
    print("send time:\t{(time.strftime("%y-%m-%d %H:%M:%S.%f"))[:-3]}")
    print("requester addr:\t{destAddr}:{}")
    print("Sequence num:\t{seqNo}")
    print("length:\t{len}")
    print("payload:\t{payload}\n")

def main():
    print("STARTED")

if __name__ == '__main__':
    main()
