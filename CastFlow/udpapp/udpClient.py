'''
Created on Nov 4, 2011

@author: arthurgodoy
'''
import sys
import socket
##import datetime
from time import time

UDP_IP=sys.argv[1] #First argument it's the binding IP
UDP_PORT=8885 #Listening port

sock = socket.socket( socket.AF_INET,     # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )

while True:
    data, addr = sock.recvfrom( 1024 )   # buffer size is 1024 bytes
    print "received on ", repr( time() ) ##datetime.datetime.now()
    print "message:", data
