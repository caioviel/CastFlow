'''
Created on Oct 23, 2011

@author: caioviel
'''

from TopologyManager import TopologyManager
from commum.Model import *
from InternalInterface import *
from ClientHandler import ClientHandler
import socket

class TopologyServer(InternalInterface):
    '''
    classdocs
    '''
    def __init__(self, topology_manager, generate_events = False, port=8887):
        '''
        Constructor
        '''
        self.startListeners = []
        self.eventListeners = []
        self.serverPort = port;
        self.topologyManager = topology_manager
        self.generate_events = generate_events;
        self.topologyManager.setEventsListener(self)
        
    def startListen(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('localhost', self.serverPort))
        self.serverSocket.listen(5)
        print 'TopplogyServer listening on port', self.serverPort, '...'
        
        while True:
            clientsocket, address = self.serverSocket.accept()
            print 'Connection received from', address
            handler = ClientHandler(self, clientsocket, address)
            handler.start()
            
    def getTopology(self):
        topology = Topology()
        topology.routers = self.topologyManager.routers
        topology.hosts = self.topologyManager.all_hosts
        topology.links = self.topologyManager.links
        return topology
    
    def getMulticastGroup(self, complete=False):
        group = Group()
        print self.topologyManager.multicast_source
        group.source = self.topologyManager.multicast_source.id
        if (complete):
            group.hosts = self.topologyManager.multicast_group
        else:
            group.hosts = self.topologyManager.active_hosts
        return group
    
    def addEventListeners(self, handler):
        if handler not in self.eventListeners:
            self.eventListeners.append(handler)
            print 'Client', handler.address, 'is listening for events.'
        else:
            print 'Client', handler.address, 'has been already listening for events.'
    
    def addStartListeners(self, handler):
        if handler not in self.startListeners:
            self.startListeners.append(handler)
            print 'Client', handler.address, 'is waiting start.'
        else:
            print 'Client', handler.address, 'has been already waiting start.'
            
    def updateTopology(self, request):
        self.topologyManager.updateHosts(request.topology.hosts)
        
    def entryEvent(self, request):
        event = None
        if request.action == request.ACTION.ENTRY_EVENT:
            event = self.topologyManager.generateEntryEvent()
        else:
            event = self.topologyManager.forceEntryEvent(request.hosts)
        if event != None:
            self.notifyEvent(event)
    
    def exitEvent(self, request):
        event = None
        if request.action == request.ACTION.EXIT_EVENT:
            event = self.topologyManager.generateExitEvent()
        else:
            event = self.topologyManager.forceExitEvent(request.hosts)
            
        if event != None:
            self.notifyEvent(event)
            
    def changeSource(self, request):
        event = None
        event = self.topologyManager.forceChangeSource(request.source)
        if event != None:
            self.notifyEvent(event)
    
    def removeHandler(self, handler):
        if handler in self.startListeners:
            self.startListeners.remove(handler)
        
        if handler in self.eventListeners:
            self.eventListeners.remove(handler)
    
    def notifyStart(self, request):
        if self.generate_events:
            if not self.topologyManager.is_running:
                self.topologyManager.startEvents()
                
        for toNotify in self.startListeners:
            notifier = AsynchronousNotifier(toNotify, request)
            notifier.doNotify()
            
    def notifyEvent(self, event):
        for toNotify in self.eventListeners:
            notifier = AsynchronousNotifier(toNotify, event)
            notifier.doNotify()
        
        