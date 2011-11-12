'''
Created on Oct 20, 2011

@author: caioviel
'''

from commum.Model import *
from topologyserver.TopologyManager import TopologyManager

if __name__ == '__main__':
        tm = TopologyManager()
        tm.importTopologyFromBrite('britefiles/brite_05_nodes.brite')
        
        print 'Multicast Source: ', tm.multicast_source.id
        
        topology = Topology()
        topology.hosts = tm.all_hosts
        topology.links = tm.links
        topology.routers = tm.routers
        
        print topology.toJson()
        
        group = Group()
        group.hosts = tm.multicast_group
        group.source = tm.multicast_source.id
              
        print '\n\n\n', group.toJson()
        
        
        
        
    