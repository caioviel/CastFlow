'''
Created on Oct 26, 2011

@author: tiagopomponet
'''
from collections import defaultdict
from commum.Model import Request, TopologyFactory
from commum.util import *
from heapq import heapify, heappop, heappush

class MST:

    def __init__(self):
        pass

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('localhost', 8887)
        s.connect( address )
        clientSocket = LongMessageSocket(s)
        return clientSocket
        
    def getTopology(self):
        request = Request()
        request.id = 1
        request.action = request.ACTION.GET_TOPOLOGY
        jsonMessage = request.toJson()
        
        clientSocket = self.connect()
        
        clientSocket.send( jsonMessage )
        jsonTopology = clientSocket.recv()
        clientSocket.close()
        self.topology = TopologyFactory().decodeJson( jsonTopology )
        return self.topology
        
    def parseTopology(self):
        edges = []
        # parseNodes
        string = ""
        for r in self.topology.routers:
            string = string + str(r.id)
        for h in self.topology.hosts:
            string = string + str(h.id)
        
        nodes = list(string)
    
        # parseLinks
        for l in self.topology.links:
            link = str(l.node1), str(l.node2), l.weight
            edges.append(link)
    
        return nodes, edges

    def prim(self, nodes, edges ):
        conn = defaultdict( list )
        for n1,n2,c in edges:
            conn[ n1 ].append( (c, n1, n2) )
            conn[ n2 ].append( (c, n2, n1) )
        mst = []
        used = set( nodes[ 0 ] )
        usable_edges = conn[ nodes[0] ][:]
        heapify( usable_edges )

        while usable_edges:
            cost, n1, n2 = heappop( usable_edges )
            if n2 not in used:
                used.add( n2 )
                mst.append( ( n1, n2, cost ) )
                for e in conn[ n2 ]:
                    if e[ 2 ] not in used:
                        heappush( usable_edges, e )
        return mst
        
    def getRemoteMST(self):
        self.topology = self.getTopology()
        self.nodes, self.edges = self.parseTopology()
        return self.prim( self.nodes, self.edges )
    
    def getMST(self, topology):
        self.topology = topology
        self.nodes, self.edges = self.parseTopology()
        return self.prim( self.nodes, self.edges )
