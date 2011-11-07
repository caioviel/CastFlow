"""mininet Custom classes

Create a custom topology from a list of switches, hosts and links (edges)

@author: arthurgodoy
"""
from commum.Model import *
from commum.util import *
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.topo import Topo, Node
import socket
import threading

class mnCustomTopology(Topo):
    "Custom topology object."

    def __init__(self, switches, hosts, links, source, clients, enable_all=True):
        "Create custom topo."

        #Host Server
        hServer = 0
        #Hosts Clients
        hClients = []
        
        # Add default members to class.
        super(mnCustomTopology, self).__init__()

        # Add switches
        for switch in switches:
            print "Adding switch ", switch.id
            self.add_node(switch.id, Node(is_switch=True))
            
        # Add hosts
        for host in hosts:
            print "Adding host ", host.id
            if host.id == source:
                print "Host is the server, ip 10.200.200.201"
                hServer = self.addHost(host.id, ip='10.200.200.201')
            elif host.id in clients:
                print "Host is a client"
                hClients.insert(host.id, self.addHost(host.id))
            else :
                print "Just another host"
                self.addHost(host.id)
                

        # Linking
        for link in links:
            print "Linking node ", link.node1,
            print " with node ", link.node2
            self.add_edge(link.node1, link.node2)

        # Consider all switches and hosts 'on'
        self.enable_all()
        #Auto start
        #self.start()

#Adding the 'topos' dict with a key/value pair to generate our newly defined
#topology enables one to pass in '--topo=mytopo' from the command line.
#topos = { 'mytopo': ( lambda: MyTopo() ) }


"""

Create a thread to init the group hosts 71636584

"""

class mnCustomGroup(threading.Thread):
    def __init__(self, topology, clientSocket):
        self.topology = topology
        self.clientSocket = clientSocket
    def run(self):
        #Sending Complete Group Request
        request = Request()
        request.id = 2
        request.action = request.ACTION.GET_COMPLETE_GROUP
        jsonMessage = request.toJson()
        print 'Sending message: ', jsonMessage
        
        self.clientSocket.send(jsonMessage)
        jsonTopology = self.clientSocket.recv()
        print 'Message received:', jsonTopology
        groupTopology = GroupFactory().decodeJson(jsonTopology)
        print 'Parsing Group Message OK.'
        
        #Create a custom topology from routers, hosts and links received in parameter "topology"
        customTopo = mnCustomTopology( self.topology.routers, self.topology.hosts, self.topology.links, groupTopology.source, groupTopology.hosts)
        customTopo.start()
    
        #Sending Wait Test Start Request    
        request.id = 4
        request.action = request.ACTION.WAIT_START
        jsonMessage = request.toJson()
        print 'Sending message: ', jsonMessage
        
        self.clientSocket.send(jsonMessage)
        
        #Waiting for Start Request    
        print 'Waiting for start...'
        jsonTopology = self.clientSocket.recv()
        print 'Message received:', jsonTopology
        topology = RequestFactory().decodeJson(jsonTopology)
        print 'Parsing Request Start Message ok.'
        
        #Start the udpapp client in each host of the client group
        for groupHost in groupTopology:
            customTopo.hClients[groupHost.id].cmdPrint('udpapp -c ' + str( customTopo.hClients[groupHost.id].IP() ) )
            
            
        #Start a udpapp server sending packages to the Multicast-Group IP on the source.
        customTopo.hServer.cmdPrint('udpapp -s 239.200.200.200')
        
        
            
