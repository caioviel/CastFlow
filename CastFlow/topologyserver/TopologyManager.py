'''
Created on Oct 21, 2011

@author: caioviel
'''

import numpy
from commum.Model import *
from BriteParser import *


class TopologyManager:
    '''
    classdocs
    '''

    def __init__(self):
        self.all_hosts = []
        self.links = []
        self.routers = []
        self.multicast_group = []
        self.active_hosts = []
        self.inactive_hosts = []
        self.multicast_source = -1
        
    def importTopologyFromBrite(self, britefile):
        parser = BriteParser(britefile)
        parser.doParse()
        self.all_hosts = parser.hosts
        self.links = parser.links
        self.routers = parser.routers
        
        self.__selectMulticastGroup__()
        
        self.multicast_source = self.selectRandomHost(self.multicast_group)
        
        self.__selectActiveHosts__()
        
        
    def selectRandomHost(self, hosts):
        host_index = int(numpy.random.uniform(0.0, len(hosts)-1))
        return hosts[host_index]
    
    def __selectMulticastGroup__(self, min_number=20.0, max_number=40.0):
        multicast_hosts_number = int(numpy.random.uniform(min_number, max_number))
    
        self.multicast_group = []
        total_hosts_number = len(self.all_hosts)
        while len(self.multicast_group) < multicast_hosts_number:
            host = self.selectRandomHost(self.all_hosts)
            if host not in self.multicast_group:
                self.multicast_group.append(host)
    
    def __selectActiveHosts__(self):
        active_hosts_number = int(numpy.random.normal(len(self.multicast_group)/2, 3.0))
        
        self.active_hosts = []
        while len(self.active_hosts) < active_hosts_number:
            host = self.selectRandomHost(self.multicast_group)
            if host == self.multicast_source:
                continue
            elif host not in self.active_hosts:
                self.active_hosts.append(host)

    
    
        
        