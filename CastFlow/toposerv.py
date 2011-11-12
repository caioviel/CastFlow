#!/usr/bin/env python
'''
Created on Oct 20, 2011

@author: caioviel
'''

import sys
from topologyserver.TopologyServer import TopologyServer

fileName = 'britefiles/brite_05_nodes.brite'
    
if (len(sys.argv) > 1):
    fileName = sys.argv[1]
        
server = TopologyServer(fileName)
server.startListen()
    