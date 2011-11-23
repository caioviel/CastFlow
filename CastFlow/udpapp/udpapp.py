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
from time import sleep
import time
import datetime

PRINT_PACKET = False
PRINT_EVENT = False
WRITE_EVENT = False

#DIRECTORY = '/tmp/logs/'
DIRECTORY = './'
FIRSTPACKET = 'FIRST_PACKET'
INTERRUPTFLOW = 'INTERRUPT_FLOW'
SOURCECHANGED = 'SOURCE_CHANGED'
RESUMEDFLOW = 'RESUMED_FLOW'
PACKETLOST = 'PACKET_LOST'

class DataCollector(object):
    def __init__(self, prename = ''):
        uuidstr = str(uuid.uuid4())
        if prename == '':
            self.filename = DIRECTORY + uuidstr + '.txt'
        else:
            self.filename = DIRECTORY + prename + '-' + uuidstr + '.txt'
        
        self.file = open(self.filename, 'w')
        
    def write_header(self, name='DataCollector', header=''):
        if header == '':
            self.file.write( name + ': ' + self.filename + '\n')
            str_time = time.strftime('%d/%m/%Y  %H:%M:%S', time.localtime() )
            self.file.write( str_time + '\n' )
        else:
            self.file.write( header + '\n' )

        #self.file.flush()
            
    def collect(self, str_data):
        self.file.write(str_data + "\n")
        self.file.flush()

class UdpAppCollector(DataCollector):
    def __init__(self, prename ='udpapp', format='csv'):
        DataCollector.__init__(self, prename)
        self.format = format
        self.csvHeader = 'SOURCE;PACKET_ID;SENDED;RECEIVED;EVENT'
        
    def write_header(self):
        if self.format == 'human':
            DataCollector.write_header(self, name ='UdpAppCollector')
        elif self.format == 'csv':
            DataCollector.write_header(self, header =self.csvHeader)
        
        
    def collect_my_ip(self, ip):
        self.collect('INSTANCE IP:' + ip + '\n')
        
    def collect_first_package(self, source_id, package_number, serv_time, local_time):
        if self.format == 'human':
            str_out = 'FIRST PACKAGE:' 
            str_out += '\n\tsource_id\t' + source_id
            str_out += '\n\tpackage_number\t' + str(package_number)
            str_out += '\n\tserv_time\t' + repr(serv_time)
            str_out += '\n\tlocal_time\t' + repr(local_time)
            self.collect(str_out + '\n')
        elif self.format == 'csv':
            self.collect(source_id +';'+ package_number +';'+ serv_time +';'+ local_time +';'+ FIRSTPACKET + '\n')
            
        self.file.flush()
        
    def collect_interrupted_flow(self, source_id, package_number, serv_time, local_time):
        if self.format == 'human':
            str_out = 'INTERRUPTED FLOW:' 
            str_out += '\n\tsource_id\t' + source_id
            str_out += '\n\tpackage_number\t' + str(package_number)
            str_out += '\n\tserv_time\t' + repr(serv_time)
            str_out += '\n\tlocal_time\t' + repr(local_time)
            self.collect(str_out + '\n')
        elif self.format == 'csv':
            self.collect(source_id +';'+ package_number +';'+ serv_time +';'+ local_time +';'+ INTERRUPTFLOW + '\n')
            
        self.file.flush()
        
    def collect_resumed_flow(self, source_id, package_number, serv_time, local_time):
        if self.format == 'human':
            str_out = 'RESUMED FLOW:' 
            str_out += '\n\tsource_id\t' + source_id
            str_out += '\n\tpackage_number\t' + str(package_number)
            str_out += '\n\tserv_time\t' + repr(serv_time)
            str_out += '\n\tlocal_time\t' + repr(local_time)
            self.collect(str_out + '\n')
        elif self.format == 'csv':
            self.collect(source_id +';'+ package_number +';'+ serv_time +';'+ local_time +';'+ RESUMEDFLOW + '\n')
        
    def collect_source_changed(self, source_id, package_number, serv_time, local_time):
        if self.format == 'human':
            str_out = 'SOURCE CHANGED:' 
            str_out += '\n\tsource_id\t' + source_id
            str_out += '\n\tpackage_number\t' + str(package_number)
            str_out += '\n\tserv_time\t' + repr(serv_time)
            str_out += '\n\tlocal_time\t' + repr(local_time)
            self.collect(str_out + '\n')
        elif self.format == 'csv':
            self.collect(source_id +';'+ package_number +';'+ serv_time +';'+ local_time +';'+ SOURCECHANGED + '\n')
        
    def collect_package_lost(self, source_id, last_package_number, current_package_number, serv_time, local_time):
        if self.format == 'human':
            str_out = 'PACKAGE LOST:'
            str_out += '\n\tsource_id\t' + source_id
            str_out += '\n\tlast_number\t' + str(last_package_number)
            str_out += '\n\tcurrent_number\t' + str(current_package_number)
            str_out += '\n\tserv_time\t' + repr(serv_time)
            str_out += '\n\tlocal_time\t' + repr(local_time)
            self.collect(str_out + '\n')
        elif self.format == 'csv':
            self.collect(source_id +';'+ package_number +';'+ serv_time +';'+ local_time +';'+ PACKETLOST + '\n')


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
            message = {'src_uuid' : SRC_UUID, 'packet_number' : str( PKT_LONG ), 'timestamp' : repr( time.time() )}
            sock.sendto(json.dumps(message), (UDP_IP, UDP_PORT) )
        
        PKT_LONG += 1
        sleep( NSECONDS )


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
    FORMAT_MODE = 'csv'
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
    if WRITE_EVENT:
        dc = UdpAppCollector(prename = 'udpapp-' + HOST_NAME + '---', format = FORMAT_MODE)

    data, addr = sock.recvfrom( 1024 )   # buffer size is 1024 bytes

    local_timestamp = repr( time.time() )
    source_id, packet_number, server_timestamp = parse_packet(data)
    if WRITE_EVENT:
        str_output = ""
        str_output += 'First Packet; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp + '\n'
        
    if PRINT_EVENT or PRINT_PACKET:
        print 'First Packet; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp

    sock.settimeout(1) #timeout setted to 1s.

    interrupted_flow = False
    current_source_id = source_id
    last_packet_number = long(packet_number)
    last_server_timestamp = float(server_timestamp)
    last_local_timestamp = float(local_timestamp)
    
    interrupted_count = 0

    while True:
        try:
            data, addr = sock.recvfrom( 1024 )   # buffer size is 1024 bytes
            local_timestamp = repr( time.time() )
            source_id, packet_number, server_timestamp = parse_packet(data)
            if interrupted_flow:
                interrupted_flow = False
                if WRITE_EVENT:
                    str_output += 'Resumed Flow; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp + '\n'
                
                if PRINT_EVENT:
                    print 'Resumed Flow; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
            
            if PRINT_PACKET:
                print source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
                
            if current_source_id != source_id:
                if WRITE_EVENT:
                    str_output += 'Source Changed; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp + '\n'
                
                if PRINT_EVENT:
                    print 'Source Changed; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
                    
            elif last_packet_number - long(packet_number) > 1:
                if WRITE_EVENT:
                    str_output += 'Packet Lost; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp + '\n'
                
                if PRINT_EVENT:
                    print 'Packet Lost; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
            
            # Save the informations
            current_source_id = source_id
            last_packet_number = long(packet_number)
            last_server_timestamp = float(server_timestamp)
            last_local_timestamp = float(local_timestamp)
            
        except socket.timeout:
            if not interrupted_flow:
                interrupted_flow = True
                interrupted_count = 0
                if WRITE_EVENT:
                    str_output += 'Interrupted Flow; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp + '\n'
                
                if PRINT_EVENT:
                    print 'Interrupted Flow; ' + source_id + '; ' + packet_number + '; ' + server_timestamp + '; ' + local_timestamp
            else:
                if WRITE_EVENT:
                    interrupted_count += 1
                    if interrupted_count == 5:
                        dc.collect(str_output)
                        str_output = ""

        
elif sys.argv[1] == "-m":
    udpserver( [ MULTICAST_IP ], UDP_PORT )

#Oops...
else:
    print "Oops..Something bad happened, check your arguments!"