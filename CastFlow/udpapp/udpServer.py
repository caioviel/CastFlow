'''
Created on Nov 4, 2011

@author: arthurgodoy
'''
import sys
import socket
##import datetime
from time import time, sleep

UDP_CLIENTS=sys.argv[1:] #Get the arguments starting from the second

UDP_PORT=8885 #Sending port

NSECONDS=0.030 #Sending period

print "UDP target IP:", UDP_CLIENTS
print "UDP target port:", UDP_PORT
print "Sending period:", NSECONDS, " seconds"

sock = socket.socket( socket.AF_INET,        # Internet
                      socket.SOCK_DGRAM )    # UDP

#Send each NSECONDS for each client
while True:
    for UDP_IP in UDP_CLIENTS:
        sock.sendto( "Sended on " + repr( time() ), ##str( datetime.datetime.now() ),
                     (UDP_IP, UDP_PORT) )
    sleep( NSECONDS )
