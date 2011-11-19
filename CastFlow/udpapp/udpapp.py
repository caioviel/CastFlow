#!/usr/bin/env python

"""
    UdpApp python script
        Server send udp packets every NSECONDS
        Client listening the UDP_PORT
        [Copy to your /usr/bin directory for call in shell]

@author: arthurgodoy
"""
import sys
import socket
import json
import uuid
from time import time, sleep
from commum.DataCollector import UdpAppCollector

UDP_PORT=8885 #Port Listening/Sending

NSECONDS=0.030 #Send Period

MULTICAST_IP = "10.0.2.254"
MULTICAST_MAC = "ca:fe:ca:fe:ca:fe"

def help():
    print " "
    print "Usage ="
    print "      Server:"
    print "              Unicast=    -s CLIENT_IP1 CLIENT_IP2 CLIENT_IPN"
    print "              Multicast=  -m"
    print "      Client:"
    print "              -c HOST_NAME"
    print "              -c HOST_NAME --format-human"
    print "              -c HOST_NAME --format-csv"
    print " "
    sys.exit()

def parse_packet(packet_data):
    parsed_data = json.loads(packet_data)
    src_uuid = parsed_data['src_uuid']
    packet_number = parsed_data['packet_number']
    timestamp = parsed_data['timestamp']
    return src_uuid, packet_number, timestamp

def udpserver( IPs, PORT ):
    SRC_UUID = str(uuid.uuid4()) #Get a UUID for this server
    PKT_LONG = long(0) #Start a packet counter
    print "SRC UUID:", SRC_UUID
    print "UDP target IP:", IPs
    print "UDP target port:", UDP_PORT
    print "Sending interval:", NSECONDS, " seconds"

    sock = socket.socket( socket.AF_INET,        # Internet
                          socket.SOCK_DGRAM )    # UDP

    #Send each NSECONDS for each client
    while True:
        for UDP_IP in IPs:
            message = {'src_uuid' : SRC_UUID, 'packet_number' : str( PKT_LONG ), 'timestamp' : repr( time() )}
            sock.sendto(json.dumps(message), (UDP_IP, UDP_PORT) )
        
        PKT_LONG += 1
        sleep( NSECONDS )


#Register the multicast ip and mac on the arp table.
#os.system('arp -s ' + MULTICAST_IP + ' ' + MULTICAST_MAC)

#Arguments should be 2 or more
if len( sys.argv ) < 2:
    help()

#Server
elif sys.argv[1] == "-s":
    UDP_CLIENTS=sys.argv[2:] #Get the arguments starting from the third
    udpserver( UDP_CLIENTS, UDP_PORT )
    
#Client
elif sys.argv[1] == "-c":
    HOST_NAME = ""
    FORMAT_MODE = 'human'
    if len(sys.argv) >= 4:
        if sys.argv[3] == "--format-csv":
            FORMAT_MODE = 'csv'
            HOST_NAME = sys.argv[2]
        elif sys.argv[3] == "--format-human":
            FORMAT_MODE = 'human'
            HOST_NAME = sys.argv[2]
        else:
            help()
    elif len(sys.argv) == 3:
        HOST_NAME = sys.argv[2]
    
    UDP_IP = ""
    
    sock = socket.socket( socket.AF_INET,     # Internet
                          socket.SOCK_DGRAM ) # UDP
    sock.bind( (UDP_IP,UDP_PORT) )
    
    uuidstr = HOST_NAME + '---' + str(uuid.uuid4())
    dc = UdpAppCollector(prename = 'udpapp-' + HOST_NAME + '---', format = FORMAT_MODE)
    
    #header = "SOURCE;PACKET_ID;SENDED;RECEIVED;"
    data, addr = sock.recvfrom( 1024 )   # buffer size is 1024 bytes
    local_timestamp = repr( time() )
    source_id, packet_number, server_timestamp = parse_packet(data)
    print source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
    dc.collect_first_package(source_id, packet_number, server_timestamp, local_timestamp)
    sock.settimeout(1) #timeout setted to 1s.
    interrupted_flow = False
    current_source_id = source_id
    last_packet_number = long(packet_number)
    last_server_timestamp = float(server_timestamp)
    last_local_timestamp = float(local_timestamp)
    while True:
        try:
            data, addr = sock.recvfrom( 1024 )   # buffer size is 1024 bytes
            local_timestamp = repr( time() )
            source_id, packet_number, server_timestamp = parse_packet(data)
            if interrupted_flow:
                interrupted_flow = False
                print 'Resumed Flow!'
                dc.collect_resumed_flow(source_id, packet_number, server_timestamp, local_timestamp)
            
            print source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
            if current_source_id != source_id:
                dc.collect_source_changed(source_id, packet_number, server_timestamp, local_timestamp)
            elif last_packet_number - long(packet_number) > 1:
                dc.collect_package_lost(source_id, str(last_packet_number), 
                                        packet_number, server_timestamp, local_timestamp)
            
            # Save the informations
            current_source_id = source_id
            last_packet_number = long(packet_number)
            last_server_timestamp = float(server_timestamp)
            last_local_timestamp = float(local_timestamp)
            
        except socket.timeout:
            if not interrupted_flow:
                interrupted_flow = True
                dc.collect_interrupted_flow(source_id, packet_number, server_timestamp, local_timestamp)
                print 'Interrupted Flow!'

        
elif sys.argv[1] == "-m":
    udpserver( [ MULTICAST_IP ], UDP_PORT )

#Oops...
else:
    print "Oops..Something bad happened, check your arguments!"