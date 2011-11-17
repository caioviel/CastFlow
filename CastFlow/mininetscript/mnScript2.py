#!/usr/bin/python

"""
This example creates a multi-controller network from
semi-scratch; note a topo object could also be used and
would be passed into the Mininet() constructor.
"""

import threading

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel

from commum.Model import *
from commum.util import *
from MyTopo import *

def initsocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('localhost', 8887)
    s.connect( address )
    return LongMessageSocket(s)

class cmdThread(threading.Thread):
    def __init__(self, objNode, strCmd):
        self.objNode = objNode
        self.strCmd = strCmd
    def run(self):
        self.objNode.cmd( self.strCmd )

def mnScript():
    "Creating a Mininet net"

    net = Mininet( controller=RemoteController, switch=OVSKernelSwitch, autoSetMacs=True, listenPort=6634 )

    print "*** Creating Remote Controller"
    c0 = net.addController( 'c0' )

    topo = MyTopo()
    
    #Build and Start
    net.buildFromTopo( topo )
    net.start()


    print "*** Starting Group ***"
    print "*** Socket"
    s = initsocket()
    
    request = Request()
    request.id = 1
    request.action = request.ACTION.GET_GROUP

    s.send (request.toJson() )
    jsonStr = s.recv()

    print "*** Group"
    group = GroupFactory().decodeJson(jsonStr)
    
    src = net.nameToNode[ "h" + str(group.source) ]
    print "*** Setup CA:FE ARP in source"
    src.cmd("arp -s 10.0.2.254 ca:fe:ca:fe:ca:fe")
    print "*** Starting udpapp in source"
    cmdThread( src, "echo blah > /home/openflow/htest" ) #"udpapp -m > " + src.name + ".log" )

    for host in group.hosts:
        h = net.nameToNode[ "h" + str(host.id) ]
        print "*** Setup CA:FE ARP in " + h.name
        h.cmd("arp -s 10.0.2.254 ca:fe:ca:fe:ca:fe")
        print "*** Starting udpapp in " + h.name
        cmdThread( h, "ping 10.0.0.1 > " + h.name + ".log") #"udpapp -c > " + h.name + ".log" )

    print "*** Starting CLI ***"
    CLI( net )

    print "*** Stopping net ***"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  
    mnScript()