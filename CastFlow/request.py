#!/usr/bin/env python

import sys

from commum.Model import *
from commum.util import *

def printGroup(group):
    print '\tTotal Hosts:', len(group.hosts)
    print '\tMulticast Source:', group.source
    print '\tHosts:',
    for host in group.hosts:
        print host.id,
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
    print jsonStr
    
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
elif request_type == 'exitGroup':
    hosts = []
    if len(sys.argv) >= 3:
        for host in sys.argv[2:]:
            hosts.append(int(host))
    exitGroup(hosts)
elif request_type == 'registerForEvents':
    registerForEvents()
else:
    print 'Invalid request type: ', request_type
    
        
    
    