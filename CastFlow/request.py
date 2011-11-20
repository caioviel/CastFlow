#!/usr/bin/env python

import sys

from commum.Model import *
from commum.util import *
from time import sleep

def printGroup(group):
    print '\tTotal Hosts:', len(group.hosts)
    print '\tMulticast Source:', group.source
    print '\tHosts:',
    hostsId = []
    for host in group.hosts:
        hostsId.append(host.id)
        
    hostsId.sort()    
    for host in hostsId:
        print host,
    print '\n'

def initsocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('localhost', 8887)
    s.connect( address )
    return LongMessageSocket(s)

def getTopology():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.GET_TOPOLOGY
    s.send (request.toJson() )
    jsonStr = s.recv()
    topology = TopologyFactory().decodeJson(jsonStr)
    for r in topology.routers:
        print '\tRouter', r.id
        for node in r.allports:
            print '\t\tport', r.getPortByNode(node),
            if topology.isHost(node):
                print ': Host', node,
            else:
                print ':Router', node,
            print '(link',  r.getLinkByNode(node), ')'
        print '\n'
            
    
def getGroup():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.GET_GROUP
    s.send (request.toJson() )
    jsonStr = s.recv()
    group = GroupFactory().decodeJson(jsonStr)
    print 'Multicast Group:'
    printGroup(group)
    
def start():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.REGISTER_FOR_EVENTS
    s.send (request.toJson() )
    
    sleep(1)
    request = Request()
    request.id = 2
    request.action = request.ACTION.START
    jsonStr = request.toJson()
    print jsonStr
    s.send ( jsonStr )
    print 'Start!'
    
    print 'Waiting for events...'
    while True:
        jsonStr = s.recv()
        event = EventFactory().decodeJson(jsonStr)
        print 'Event Received:'
        print '\tType:', event.type
        if event.type == 'changeSource':
            print '\nNew Source:', event.source
        else:
            print '\tHosts:',
            for host in event.hosts:
                print host.id,
            print '\n'

def entryEvent():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.ENTRY_EVENT
    s.send (request.toJson() )

def exitEvent():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.EXIT_EVENT
    s.send (request.toJson() )

def sourceEvent():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.SOURCE_EVENT
    s.send (request.toJson() )
    
def getCompleteGroup():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.GET_COMPLETE_GROUP
    s.send (request.toJson() )
    jsonStr = s.recv()
    group = GroupFactory().decodeJson(jsonStr)
    print 'Complete Multicast Group:'
    printGroup(group)
    
def entryGroup(hosts):
    s = initsocket()
    request = Request()
    request.id = 1
    request.hosts = hosts
    request.action = request.ACTION.ENTRY_GROUP
    s.send (request.toJson() )
    jsonStr = s.recv()
    event = EventFactory().decodeJson(jsonStr)
    print 'Entry Event:'
    print '\tHosts:',
    for host in event.hosts:
        print host.id,
    print '\n'
    
def exitGroup(hosts):
    s = initsocket()
    request = Request()
    request.id = 1
    request.hosts = hosts
    request.action = request.ACTION.EXIT_GROUP
    s.send (request.toJson() )
    jsonStr = s.recv()
    event = EventFactory().decodeJson(jsonStr)
    print 'Exit Event:'
    print '\tHosts:',
    for host in event.hosts:
        print host.id,
    print '\n'
    
def changeSource(source):
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.CHANGE_SOURCE
    request.source = source
    s.send( request.toJson() )
    jsonStr = s.recv()
    event = EventFactory().decodeJson(jsonStr)
    print 'Change Source Event:'
    print '\tNew Source:', event.source
    print '\n'

def registerForEvents():
    s = initsocket()
    request = Request()
    request.id = 1
    request.action = request.ACTION.REGISTER_FOR_EVENTS
    s.send (request.toJson() )
    print 'Waiting for events...'
    while True:
        jsonStr = s.recv()
        event = EventFactory().decodeJson(jsonStr)
        print 'Event Received:'
        print '\tType:', event.type
        if event.type == 'changeSource':
            print '\nNew Source:', event.source
        else:
            print '\tHosts:',
            for host in event.hosts:
                print host.id,
                print '\n'

if len(sys.argv) < 2:
    print 'Please, inform the request type.'
    sys.exit()
    
request_type = sys.argv[1]

if request_type == 'getTopology':
    getTopology()
elif request_type == 'start':
    start()
elif request_type == 'entryEvent':
    entryEvent()
elif request_type == 'exitEvent':
    exitEvent()
elif request_type == 'sourceEvent':
    sourceEvent()
elif request_type == 'getGroup':
    getGroup()
elif request_type == 'getCompleteGroup':
    getCompleteGroup()
elif request_type == 'entryGroup':
    hosts = []
    if len(sys.argv) >= 3:
        for host in sys.argv[2:]:
            hosts.append(int(host))
            
        entryGroup(hosts)
    else:
        print 'Please, say the hosts.'
elif request_type == 'exitGroup':
    hosts = []
    if len(sys.argv) >= 3:
        for host in sys.argv[2:]:
            hosts.append(int(host))
        
        exitGroup(hosts)
    else:
        print 'Please, say the hosts.'
elif request_type == 'registerForEvents':
    registerForEvents()
elif request_type == 'changeSource':
    if len(sys.argv) >= 3:
        changeSource( int(sys.argv[2]) )
    else:
        print 'Please, say the new source'
else:
    print 'Invalid request type: ', request_type
    
        
    
    