"""Custom topology example

author: Brandon Heller (brandonh@stanford.edu)

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo, Node
from commum.Model import *
from commum.util import *

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self, enable_all = True ):
        "Create custom topo."
        # Add default members to class.
        super( MyTopo, self ).__init__()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('localhost', 8887)
        print 'Trying to connect on server', address
        s.connect( address )
        print 'Connection successed!'
    
        clientSocket = LongMessageSocket(s)
    
        #Sending Topology Request
    
        request = Request()
        request.id = 1
        request.action = request.ACTION.GET_TOPOLOGY
        jsonMessage = request.toJson()
        
        clientSocket.send(jsonMessage)
        jsonTopology = clientSocket.recv()
        print 'Message received:', jsonTopology
        topology = TopologyFactory().decodeJson(jsonTopology)
        
        for router in topology.routers:
            self.add_node( router.id, Node (is_switch=True))
            
        for host in topology.hosts:
            self.add_node( host.id, Node (is_switch=False))
            
        for link in topology.links:
            self.add_edge (link.node1, link.node2)

        # Consider all switches and hosts 'on'
        self.enable_all()


topos = { 'mytopo': ( lambda: MyTopo() ) }