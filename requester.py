import argparse
import socket
from datetime import datetime
import sys

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

# open file to write to
# this also creates a file assuming it is not there or overwrites it if it exists
toWrite = open(args.fileName, 'w')

# track size of file written and end size of file
finalSizeBytes = 0
currSizeBytes = 0

def printPacket(ptype, time, srcAddr, srcPort, seq, length, percent, payload):
    print(f"{ptype} Packet")
    timeStr = (time.strftime("%y-%m-%d %H:%M:%S.%f"))[:-3]
    print(f"recieve time:\t{timeStr}")
    print(f"sender addr:\t{srcAddr}:{srcPort}")
    print(f"sequence:\t{seq}")
    print(f"length:\t\t{length}")
    if (ptype == "DATA"):
        print(f"percentage:{percent:^12,.2%}")
        print(f"payload:\t{payload[0:4].decode('utf-8')}\n")
    else:
        print(f"payload:\t\n")


# function to send request to specified sender
def sendReq(destIP, port):
    pt = b'R'
    seq = 0
    l = len(args.fileName)

    header = pt + socket.htonl(seq).to_bytes(4, 'big') + socket.htonl(l).to_bytes(4, 'big')
    payload = args.fileName.encode('utf-8')
    packet = header + payload
    soc.sendto(packet, (destIP, port))

# function to readd the tracker
# Assumed name is tracker.txt
def readTracker():
    # create dictionary with file names
    global files
    files = dict()

    # first pass to get size for arrays of tuples of data
    with open("tracker.txt", 'r') as tracker:
        line = tracker.readline()
        while line:
            vals = line.split()

            # check if the value exists in the dictionary
            if files.get(vals[0]) is None:
                files[vals[0]] = list()
            # add string values to array
            files[vals[0]].append((vals[1], vals[2], vals[3], vals[4]))

            # get new line
            line = tracker.readline()

        # sort values in arrays for each file
        for k in files.keys():
            # array to replace old array
            tempArr = [(0,0,0)] * len(files[k])

            # iterate over each element and place it in the right spot
            for t in files[k]:
                spot = int(t[0]) - 1
                # convert host name to ip, port to int, remove b from bytes to int
                tempArr[spot] = (socket.gethostbyname(t[1]), int(t[2]), int(t[3][:-1]))
            # replace old array with the new one
            files[k] = tempArr


# handles a packet from sender
# returns false if it gets something other than data packet (End packet)
# returns true if it gets a data packet
def handlePacket(data, addr, time):
    # get header values
    pType = data[0]
    seqNo = socket.ntohl(int.from_bytes(data[1:5], 'big'))
    pLen = socket.ntohl(int.from_bytes(data[5:9], 'big'))

    # check packet type
    # End type
    if (pType.to_bytes(1, 'big') == b'E'):
        printPacket("End", time, addr[0], addr[1], seqNo, pLen, 0, 0)
        return False
    elif (pType.to_bytes(1, 'big') != b'D'):
        # something went wrong
        return False
    # Data packet

    payload = data[9:9 + pLen]
    toWrite.write(payload.decode('utf-8'))
    # add bytes written and print packet info
    global currSizeBytes
    currSizeBytes += pLen
    global finalSizeBytes
    printPacket("DATA", time, addr[0], addr[1], seqNo, pLen, currSizeBytes / finalSizeBytes, payload)
    return True

# fucntion to listen for packets and send packets elsewhere
def waitListen():
    isListening = True
    while isListening:
        data, addr = soc.recvfrom(2048)
        print(data)
        isListening = handlePacket(data, addr, datetime.now())

def getFile(fileName):
    # get size of the file
    for s in files[fileName]:
        global finalSizeBytes 
        finalSizeBytes += s[2]

    # iterate over senders to get file from
    for s in files[fileName]:
        # send request to sender
        print(f"bals: {s[0]}")
        sendReq(s[0], s[1])
        # wait for and handle to packets
        waitListen()

# function to clean and close all parts of the project
def cleanup():
    toWrite.close()
    soc.close()
    sys.exit()

def main():
    print("START REQUESTER")
    # get files to get
    readTracker()
    # check that file name is in files/tracker
    if args.fileName not in files.keys():
        print("FILE NOT FOUND IN TRACKER")
        return -1
    # get the file
    getFile(args.fileName)
    cleanup()

if __name__ == '__main__':
    main()
