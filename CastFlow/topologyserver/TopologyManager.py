'''
Created on Oct 21, 2011

@author: caioviel
'''

from commum.Model import *
from BriteParser import *
import numpy

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
        
        selectMulticastGroup()
        self.multicast_source = self.selectRandomHost(self.multicast_group)
        
        
    def selectRandomHost(self, hosts):
        host_index = int(numpy.random.uniform(0.0, len(hosts)-1))
        return hosts[host_index]
    
    def selectMulticastGroup(self, min_number=20.0, max_number=40.0):
        multicast_hosts_number = int(numpy.random.uniform(min_number, max_number))
    
        self.multicast_group = []
        total_hosts_number = len(self.all_hosts)
        while len(multicast_hosts_set) < multicast_hosts_number:
            host = self.selectRandomHost(self.all_hosts)
            if host not in self.multicast_group:
                self.multicast_group.append(host)
    
    def selectActiveHosts(self):
        pass
    
    
        
        