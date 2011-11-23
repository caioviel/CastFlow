'''
Created on Nov 13, 2011

@author: caioviel
'''

import uuid
import time

DIRECTORY = '/tmp/logs/'
FIRSTPACKET = 'FIRST_PACKET'
INTERRUPTFLOW = 'INTERRUPT_FLOW'
SOURCECHANGED = 'SOURCE_CHANGED'
RESUMEDFLOW = 'RESUMED_FLOW'
PACKETLOST = 'PACKET_LOST'

from commum.Model import Event, Host

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
        #self.file.flush()

class NoxAppCollector(DataCollector):
    def __init__(self, prename='noxapp'):
        DataCollector.__init__(self, prename)
        self.str_out = ""
        
    def write_header(self):
        DataCollector.write_header(self, 'NoxAppCollector')
        
    def collect_begin_mst(self, total_nodes, time):
        str_out = 'BEGIN MST:' 
        str_out += '\n\ttotal_nodes\t' + repr(total_nodes)
        str_out += '\n\ttime\t\t' + repr(time)
        self.str_out += str_out + '\n'
        #self.collect(str_out + '\n')
    
    def collect_end_mst(self, total_nodes, time):
        str_out = 'END MST:' 
        str_out += '\n\ttotal_nodes\t' + repr(total_nodes)
        str_out += '\n\ttime\t\t' + repr(time)
        self.str_out += str_out + '\n'
        #self.collect(str_out + '\n')
    
    def collect_begin_paths(self, total_nodes, time):
        str_out = 'BEGIN PATHS:' 
        str_out += '\n\ttotal_nodes\t' + repr(total_nodes)
        str_out += '\n\ttime\t\t' + repr(time)
        self.str_out += str_out + '\n'
        #self.collect(str_out + '\n')
    
    def collect_end_paths(self, total_nodes, time):
        str_out = 'END PATHS:' 
        str_out += '\n\ttotal_nodes\t' + repr(total_nodes)
        str_out += '\n\ttime\t\t' + repr(time)
        self.str_out += str_out + '\n'
        #self.collect(str_out + '\n')
    
    def collect_begin_installing_flows(self, total_nodes, active_nodes, time):
        str_out = 'BEGIN INSTALLING FLOWS:' 
        str_out += '\n\ttotal_nodes\t' + str(total_nodes)
        str_out += '\n\tactive_nodes\t' + str(active_nodes)
        str_out += '\n\ttime\t\t' + repr(time)
        self.str_out += str_out  + '\n'
        #self.collect(str_out + '\n')
    
    def collect_end_installing_flows(self, total_nodes, active_nodes, time):
        str_out = 'END INSTALLING FLOWS:' 
        str_out += '\n\ttotal_nodes\t' + str(total_nodes)
        str_out += '\n\tactive_nodes\t' + str(active_nodes)
        str_out += '\n\ttime\t\t' + repr(time) 
        self.str_out += str_out + '\n'
        self.collect(self.str_out + '\n')
        self.str_out = ""
        self.file.flush()
    
    def collect_event_effects(self, event, routes_to_install, routes_to_remove, time, ):
        str_out = ''
        if event == None:
            str_out +='INITIALIZATION:'
        elif event.type == 'entry' or event.type == 'exit':
            str_out += 'EVENT:'
            str_out +='\n\tevent_id:' + str(event.id)
            str_out +='\n\tevent_type\t' + event.type
            str_out +='\n\thosts:\t\t'
            for host in event.hosts:
                str_out += str(host.id) + ' '
        elif event.type == 'changeSource':
            str_out += 'EVENT:'
            str_out +='\n\tevent_id:' + str(event.id)
            str_out +='\n\tevent_type\t' + event.type
            str_out +='\n\tnew_source\t' + str(event.source)
        
        str_out += '\n\tinstalls\t' + str(routes_to_install)
        str_out += '\n\tremoves\t' + repr(routes_to_remove)
        str_out += '\n\ttime\t\t' + repr(time)
        self.str_out += str_out + '\n'
        #self.collect(str_out + '\n')

class UdpAppCollector(DataCollector):
    def __init__(self, prename ='udpapp', format='human'):
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

'''            
if __name__ == '__main__':
    data = UdpAppCollector()
    data.write_header()
    data.collect_my_ip('10:0:0:51')
    data.collect_first_package('fonte1', 1, 121321, 1231213321)
    data.collect_package_lost('fonte1', 1, 3, 45465465, 45646546)
    data.collect_interrupted_flow('fonte1', 4, 213213, 313123123)
    data.collect_resumed_flow('fonte1', 10, 2312321, 321312312)
    data.collect_source_changed('fonte2', 1, 121212, 2121212)
    
    data = NoxAppCollector()
    data.write_header()
    data.collect_begin_mst(10, 454654)
    data.collect_end_mst(10, 456456456)
    data.collect_begin_paths(10, 454654)
    data.collect_end_paths(10, 456456456)
    data.collect_event_effects(None, 10, 0, 454654654)
    data.collect_begin_installing_flows(50, 20, 12313213)
    data.collect_end_installing_flows(50, 20, 121231321)
    
    host = Host()
    host.id = 1
    
    event = Event(1, "entry")
    event.hosts.append(host)
    data.collect_event_effects(event, 4, 0, 12121121)
    data.collect_begin_installing_flows(50, 23, 12313213)
    data.collect_end_installing_flows(50, 23, 121231321)
    
    event = Event(2, "exit")
    event.hosts.append(host)
    data.collect_event_effects(event, 1, 3, 12121121)
    data.collect_begin_installing_flows(50, 20, 12313213)
    data.collect_end_installing_flows(50, 20, 121231321)
    
    event = Event(3, "changeSource")
    event.source = 10
    data.collect_event_effects(event, 7, 5, 12121121)
    data.collect_begin_installing_flows(50, 20, 12313213)
    data.collect_end_installing_flows(50, 20, 121231321)
'''    