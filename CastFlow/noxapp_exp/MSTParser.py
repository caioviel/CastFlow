'''
Created on Nov 12, 2011

@author: caioviel
'''

from collections import defaultdict
from commum.Model import Topology
from heapq import heapify, heappop, heappush

class MSTParser:
    def __init__(self, topology, source):
        self.topology = self.__clean_topology__(topology)
        
        #Calcule the weight of the links
        self.__calcLinksWeight__( source )
        
        #Parse the topology
        self.parse_topology()
    
    def __clean_topology__(self, topology):
        for router in topology.routers:
            router.distanceFromSource = -1
            
        for link in topology.links:
            link.weight = -1
        
        return topology
        
    def parse_topology(self):
        edges = []
        # parseNodes
        string = ""
        for r in self.topology.routers:
            string = string + str(r.id)
        for h in self.topology.hosts:
            string = string + str(h.id)
        
        nodes = list(string)
            
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
    
    
    def __calcLinksWeight__(self, source):
        visitedNodes = []
        nodesToVisit = []
        link = self.topology.getLinkById(source.link)
        source.distanceFromSource = 0
        link.weight = 1
        node = self.topology.getRouterById(source.router)

        node.distanceFromSource = 1
        
        visitedNodes.append(source.id)
        nodesToVisit.append(node)
        
        while len(nodesToVisit) > 0:
            node = nodesToVisit.pop(0)
            if node.id in visitedNodes:
                #It's had already been calculed.
                continue
            
            visitedNodes.append(node.id)
            
            if self.topology.isHost(node.id):
                #it's a host
                host = node
                link = self.topology.getLinkById(host.link)
                if link.weight == -1: 
                    #The weight for this link hasn't been calculed
                    link.weight = node.distanceFromSource + 1
                elif link.weight > node.distanceFromSource + 1:
                    link.weight = node.distanceFromSource + 1
                
                router = self.topology.getRouterById(host.router)
                if router.distanceFromSource == -1:
                    router.distanceFromSource = link.weight
                elif router.distanceFromSource > link.weight:
                    router.distanceFromSource = link.weight
                
                nodesToVisit.append(router)   
                
            else: 
                #It's a router
                thisrouter = node
                for i in range(len(thisrouter.allports)):
                    link = self.topology.getLinkById( thisrouter.links[i] )
                    nodeid = thisrouter.allports[i]
                    
                    if link.weight == -1: 
                    #The weight for this link hasn't been calculed
                        link.weight = thisrouter.distanceFromSource + 1
                    elif link.weight > thisrouter.distanceFromSource + 1:
                        link.weight = thisrouter.distanceFromSource + 1
                    
                    _node = None
                    if self.topology.isHost(nodeid):
                        _node = self.topology.getHostById(nodeid)
                    else:
                        _node = self.topology.getRouterById(nodeid)
                        
                    if _node.distanceFromSource == -1:
                        _node.distanceFromSource = link.weight
                    elif _node.distanceFromSource > link.weight:
                        _node.distanceFromSource = link.weight
                
                    nodesToVisit.append(_node)