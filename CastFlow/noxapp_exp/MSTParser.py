'''
Created on Nov 12, 2011

@author: caioviel
'''

from collections import defaultdict
from commum.Model import Topology
from heapq import heapify, heappop, heappush

class MSTParser:
    def __init__(self, topology):
        self.topology = topology
        self.parse_topology()
        
    def parse_topology(self):
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
    
        self.nodes = nodes
        self.edges = edges
    
    def __prim_algorithm__(self, nodes, edges ):
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
    
    def get_mst(self, algorithm = 'prim'):
        return self.__prim_algorithm__(self.nodes, self.edges)