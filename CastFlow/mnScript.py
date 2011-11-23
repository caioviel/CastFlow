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
from time import sleep

def initsocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('localhost', 8887)
    s.connect( address )
    return LongMessageSocket(s)

def mnScript():
    "Creating a Mininet net"

    net = Mininet( controller=RemoteController, switch=OVSKernelSwitch, autoSetMacs=True, listenPort=7001 )

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
    #request.action = request.ACTION.GET_COMPLETE_GROUP

    s.send (request.toJson() )
    jsonStr = s.recv()

    print "*** Group"
    group = GroupFactory().decodeJson(jsonStr)
    
    src = net.nameToNode[ "h" + str(group.source) ]
    print "*** Setup CA:FE ARP in source:", src.name
    src.cmd("arp -s 10.0.2.254 ca:fe:ca:fe:ca:fe")
    print "*** Start udpapp in source( " + src.name + " ) manually ;)"
    #src.cmd("udpapp -m &")
    
    for host in group.hosts:
        if host.id != group.source:
            h = net.nameToNode[ "h" + str(host.id) ]
            print "*** Setup CA:FE ARP in " + h.name
            h.cmd("arp -s 10.0.2.254 ca:fe:ca:fe:ca:fe")
            print "*** Starting udpapp in " + h.name
            #h.cmd("udpapp -c " + h.name  + " &")
            #sleep( 1 )

    print "*** Starting CLI ***"
    CLI( net )

    print "*** Stopping net ***"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  
    mnScript()