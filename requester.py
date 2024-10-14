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
    pt = b'R'
    seq = 0
    l = 0

    header = pt + seq.to_bytes(4, 'big') + l.to_bytes(4, 'big')
    soc.sendto(header, (destIP, port))

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

def getFile(fileName):
    #iterate over senders to get file from
    for s in files[fileName]:
        # send request to sender
        sendReq(s[0], s[1])
        print("REQ SENT")
    

def main():
    print("START REQUESTER")
    # get files to get
    readTracker()
    # for each file get the file
    for fileName in files.keys():
        getFile(fileName)

if __name__ == '__main__':
    main()
