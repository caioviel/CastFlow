'''
Created on Oct 21, 2011

@author: caioviel
'''

import numpy
import threading
import time

from commum.Model import *
from InternalInterface import InternalInterface
from BriteParser import BriteParser


class TopologyManager(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.all_hosts = []
        self.links = []
        self.routers = []
        self.multicast_group = []
        self.active_hosts = []
        self.inactive_hosts = []
        self.multicast_source = None
        self.eventListener = None
        self.is_running = False
        self.event_id = 0
        
        self.entry_number = 1
        self.entry_poisson = False
        self.exit_number = 1
        self.exit_poisson = False
        self.interval_mediam = 40
        self.intera_stddev = 5
        
    def set_entry_events(self, entry_number, use_poisson = False):
        self.entry_number = entry_number
        self.entry_poisson = use_poisson
        
    def set_exit_events(self, exit_number, use_poisson = False):
        self.exit_number = exit_number
        self.exit_poisson = use_poisson
        
    def set_event_interval(self, interval_mediam, interval_stddev=5):
        self.interval_mediam = interval_mediam
        self.intera_stddev = interval_stddev
        
        
    def getNextEventId(self):
        self.event_id += 1 
        return self.event_id
        
    def importTopologyFromBrite(self, britefile, group_size=0, initial_group_size=0, initial_source=0, delta_id=1):        
        parser = BriteParser(britefile, delta_id)
        parser.doParse()
        self.all_hosts = parser.hosts
        self.links = parser.links
        self.routers = parser.routers
        
        print 'Parser Done: routers', len(self.routers), ' | hosts', len(self.all_hosts), ' | links', len(self.links)
        hosts_numbers = len(self.all_hosts)
        
        if group_size != 0:
            if hosts_numbers < group_size:
                raise Exception('Demanded group is bigger than the topology!')
            else:
                if initial_source != 0:
                    if not self.isHost(initial_source):
                        raise Exception('Demanded source is invalid!')
                    
                    self.multicast_source = self.getHostById(initial_source)
                    self.multicast_group.append(self.multicast_source)
                    if group_size >= 2:
                        self.__selectMulticastGroup__(group_size-1)
                else:
                    self.__selectMulticastGroup__(group_size)
                    self.multicast_source = self.selectRandomHost(self.multicast_group)
                    
        else:
            self.__selectMulticastGroup__(hosts_numbers/2 +1)
            self.multicast_source = self.selectRandomHost(self.multicast_group)
            
            
        print 'Multicast Group Selected:', len(self.multicast_group), 'hosts'
        print 'Multicast Source: ', self.multicast_source
                
        
        if initial_group_size != 0:
            if group_size - 1 < initial_group_size:
                raise Exception('Initial group size is bigger than the group size')
            else:
                self.__selectActiveHosts__( initial_group_size )
                
        else:
            self.__selectActiveHosts__( (len(self.multicast_group)-1) / 2)
        
        print 'Active Hosts Selected:', len(self.active_hosts), 'hosts'
        #self.__calcLinksWeight__()
        #print 'Links Weight Calculated'
        
        
    def selectRandomHost(self, hosts):
        host_index = int(numpy.random.uniform(0.0, len(hosts)-1))
        return hosts[host_index]
    
    def __selectMulticastGroup__(self, group_soze):
        multicast_hosts_number = group_soze
    
        self.multicast_group = []
        while len(self.multicast_group) < multicast_hosts_number:
            host = self.selectRandomHost(self.all_hosts)
            if host not in self.multicast_group:
                self.multicast_group.append(host)
    
    def __selectActiveHosts__(self, active_hosts_number):
        #active_hosts_number = len(self.multicast_group)
        #while active_hosts_number >= len(self.multicast_group) -1 or active_hosts_number == 0:
        #    active_hosts_number = int(numpy.random.normal(len(self.multicast_group)/2, 1.0))
        
        if active_hosts_number == 0:
            return
        
        self.active_hosts = []
        while len(self.active_hosts) < active_hosts_number:
            host = self.selectRandomHost(self.multicast_group)
            if host == self.multicast_source:
                continue
            elif host not in self.active_hosts:
                self.active_hosts.append(host)
        
        for host in self.multicast_group:
            if host == self.multicast_source:
                continue
            elif host not in self.active_hosts:
                self.inactive_hosts.append(host)
                
    def setEventsListener(self, eventListener):
        self.eventListener = eventListener
    
    def startEvents(self):
        if self.eventListener == None:
            raise Exception("Trying to start the event generation without setting the events listener.")
        else:
            self.is_running = True
            threading.Thread.start(self)
            
    def run(self):
        print 'Starting to generate events...'
        generate_exit = True
        while self.is_running:
            #Dormir um tempo aleatorio seguindo uma distrubuicao normal de media 40 e variancia 5 (em segundos)
            #sleepingTime = 0
            #while sleepingTime <= 0:
            #    sleepingTime = numpy.random.normal(self.interval_mediam, self.interval_mediam)
            print 'Sleeping for', self.interval_mediam
            time.sleep(self.interval_mediam)
            
            #50% de chances de ser um evento de entrada / 50% de ser um evento de saida
            #event = None
            #value = numpy.random.random()
            #if value >= 0.5: #Evento de entrada
            #    event = self.generateEntryEvent()
            #else: #Evento de saida
            #    event = self.generateExitEvent()
            
            event = None
            if generate_exit:
                event = self.generateExitEvent()
            else:
                event = self.generateEntryEvent()
                
            generate_exit = not generate_exit
            #print event.hosts
            
            if len(event.hosts) > 0:
                print 'Event generated.'
                self.eventListener.notifyEvent(event)
            
    def generateEntryEvent(self):
        entering_hosts = []
        entering_hosts_number = self.entry_number
        if self.entry_poisson:
            entering_hosts_number = numpy.random.poisson(self.entry_number);
            
        while len(entering_hosts) < entering_hosts_number:
            host = self.selectRandomHost(self.inactive_hosts)
            if host not in entering_hosts:
                entering_hosts.append(host)
                
        for host in entering_hosts:
            self.active_hosts.append(host)
            self.inactive_hosts.remove(host)
                
        event = Event(self.getNextEventId(), 'entry')
        event.hosts = entering_hosts
        return event
    
    def generateExitEvent(self):
        exiting_hosts = []
        exiting_hosts_number = self.exit_number
        if self.exit_poisson:
            exiting_hosts_number = numpy.random.poisson(self.poissonExit);
            
        while len(exiting_hosts) < exiting_hosts_number:
            host = self.selectRandomHost(self.active_hosts)
            if host not in exiting_hosts:
                exiting_hosts.append(host)
                
        for host in exiting_hosts:
            self.inactive_hosts.append(host)
            self.active_hosts.remove(host)
                
        event = Event(self.getNextEventId(), 'exit')
        event.hosts = exiting_hosts
        return event
    
    def forceEntryEvent(self, hosts):
        if hosts == []:
            return self.generateEntryEvent()
        else:
            hosts_to_entry = []
            for host in hosts:
                print 'ForceEntryEvent:', host
                host_to_entry = self.getHostById(host)
                if host_to_entry in self.active_hosts:
                    print 'Host', host, 'is already in the multicast group'
                    return None
                hosts_to_entry.append(host_to_entry)
                
            for host in hosts_to_entry:
                self.active_hosts.append(host)
                self.inactive_hosts.remove(host)
                
            event = Event(self.getNextEventId(), 'entry')
            event.hosts = hosts_to_entry
            return event
        
    def forceExitEvent(self, hosts):
        if hosts == []:
            return self.generateExitEvent()
        else:
            hosts_to_exit = []
            for host in hosts:
                host_to_exit = self.getHostById(host)
                if host_to_exit in self.inactive_hosts:
                    print "Host", host,  "isn't in the multicast group"
                    return None
                hosts_to_exit.append(host_to_exit)
                
            for host in hosts_to_exit:
                self.inactive_hosts.append(host)
                self.active_hosts.remove(host)
                
            event = Event(self.getNextEventId(), 'exit')
            event.hosts = hosts_to_exit
            return event
        
    def forceChangeSource(self, new_source_id):
        print 'forceChangeSource'
        source_host = self.getHostById(new_source_id)
        if source_host in self.multicast_group:
            #The new new_source_id must be in the multicast group
            if source_host in self.active_hosts:
                #The new new_source_id won't be a active source_host
                self.active_hosts.remove(source_host)
                
            #The old new_source_id will be a inactive source_host
            old_source = self.getHostById( self.multicast_source )
            self.inactive_hosts.append(old_source)
            self.multicast_source = source_host
            
            event = Event(self.getName(), 'changeSource')
            event.source = new_source_id
            return event
        
        return None
        
    
    def isHost(self, nodeid):
        if nodeid > len(self.routers):
            return True
        else:
            return False
        
    def getHostById(self, hostId):
        if self.isHost(hostId):
            return self.all_hosts[hostId - (len(self.routers)+1) ]
        else:
            return None
        
    def getRouterById(self, routerId):
        if not self.isHost(routerId):
            return self.routers[routerId-1]
        else:
            print 'Will return None.'
            return None
        
    def getLinkById(self, linkid):
        return self.links[linkid-1]
    
    def updateHosts(self, hosts):
        for i in range(len(self.all_hosts)):
            self.all_hosts[i].ip = hosts[i].ip
            self.all_hosts[i].mac = hosts[i].mac
        
    
    def __calcLinksWeight__(self):
        visitedNodes = []
        nodesToVisit = []
        source = self.multicast_source
        link = self.getLinkById(source.link)
        source.distanceFromSource = 0
        link.weight = 1
        node = self.getRouterById(source.router)

        node.distanceFromSource = 1
        
        visitedNodes.append(source.id)
        nodesToVisit.append(node)
        
        while len(nodesToVisit) > 0:
            node = nodesToVisit.pop(0)
            if node.id in visitedNodes:
                #It's had already been calculed.
                continue
            
            visitedNodes.append(node.id)
            
            if self.isHost(node.id):
                #it's a host
                host = node
                link = self.getLinkById(host.link)
                if link.weight == -1: 
                    #The weight for this link hasn't been calculed
                    link.weight = node.distanceFromSource + 1
                elif link.weight > node.distanceFromSource + 1:
                    link.weight = node.distanceFromSource + 1
                
                router = self.getRouterById(host.router)
                if router.distanceFromSource == -1:
                    router.distanceFromSource = link.weight
                elif router.distanceFromSource > link.weight:
                    router.distanceFromSource = link.weight
                
                nodesToVisit.append(router)   
                
            else: 
                #It's a router
                thisrouter = node
                for i in range(len(thisrouter.allports)):
                    link = self.getLinkById( thisrouter.links[i] )
                    nodeid = thisrouter.allports[i]
                    
                    if link.weight == -1: 
                    #The weight for this link hasn't been calculed
                        link.weight = thisrouter.distanceFromSource + 1
                    elif link.weight > thisrouter.distanceFromSource + 1:
                        link.weight = thisrouter.distanceFromSource + 1
                    
                    _node = None
                    if self.isHost(nodeid):
                        _node = self.getHostById(nodeid)
                    else:
                        _node = self.getRouterById(nodeid)
                        
                    if _node.distanceFromSource == -1:
                        _node.distanceFromSource = link.weight
                    elif _node.distanceFromSource > link.weight:
                        _node.distanceFromSource = link.weight
                
                    nodesToVisit.append(_node)