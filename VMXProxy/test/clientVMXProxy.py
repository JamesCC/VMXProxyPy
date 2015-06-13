import socket
import sys
import time
import random

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def sendAssertReply(command, expectedReply):
    reply = sendGetReply(command)
    assert reply == chr(2)+expectedReply+";"

def sendGetReply(command):
    reply = ''
    try:
        message = chr(2) + command + ';'
        sock.sendall(message)
        while len(reply)==0 or reply[-1] != ';':
            reply += sock.recv(64)

    except socket.timeout:
        reply = None
    
    if reply:
        reply = reply.replace(chr(6),"<ack>")
        reply = reply.replace(chr(2),"<stx>")

    return reply


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
sock.settimeout(3)

dict = {}
for loop in xrange(100,0,-1):

    for i in range(32):
        inputID = "I"+str(i+1)
        command = ""
        command += "CNq:"+inputID+"&"
        command += "PIq:"+inputID+"&"
        command += "MUq:"+inputID+"&"
        command += "FDq:"+inputID

        reply = sendGetReply( command )
        expectedReply = dict.get(inputID, "")
        if expectedReply:
            assert reply == expectedReply
            sys.stdout.write('.')
            sys.stdout.flush()
        else:
            dict[inputID] = reply
            print bcolors.OKBLUE + command + bcolors.ENDC
            print bcolors.OKGREEN + reply + bcolors.ENDC

    command = ""
    for i in range(8):
        inputID = "AX"+str(i+1)
        command += "CNq:"+inputID+"&"
    command += "SCq"
    reply = sendGetReply( command )
    expectedReply = dict.get(inputID, "")
    if expectedReply:
        assert reply == expectedReply
        sys.stdout.write('.')
        sys.stdout.flush()
    else:
        dict[inputID] = reply
        print bcolors.OKBLUE + command + bcolors.ENDC
        print bcolors.OKGREEN + reply + bcolors.ENDC

    delay = 5 + random.random()
    print( "  %gs [%d]" % (delay, loop) )
    time.sleep( delay )

print >>sys.stderr, 'closing socket'
sock.close()
