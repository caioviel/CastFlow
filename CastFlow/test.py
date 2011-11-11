'''
Created on Oct 20, 2011

@author: caioviel
'''

from commum.Model import *
from topologyserver.TopologyManager import TopologyManager

if __name__ == '__main__':
        tm = TopologyManager()
        tm.importTopologyFromBrite('brite1.brite')
        
        print 'Multicast Source: ', tm.multicast_source.id
        
        topology = Topology()
        topology.hosts = tm.all_hosts
        topology.links = tm.links
        topology.routers = tm.routers
        
        print topology.toJson()
        
        
        
        
    