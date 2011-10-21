'''
Created on Oct 20, 2011

@author: caioviel
'''


from Model import *
from BriteParser import BriteParser

if __name__ == '__main__':
    parser = BriteParser('brite1.brite')
    parser.doParse()
    topology = Topology()
    topology.hosts = parser.hosts
    topology.links = parser.links
    topology.routers = parser.routers
    
    jsonMessage = topology.toJson()
    topology = TopologyFactory().decodeJson(jsonMessage)
    print jsonMessage
    
    
    
    
    