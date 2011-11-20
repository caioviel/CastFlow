from commum.util import LongMessageSocket
from commum.Model import *
from InternalInterface import InternalInterface
import threading

class ClientHandler(threading.Thread):
    def __init__(self, topologyServer, socket, address):
        threading.Thread.__init__(self)
        self.socket = LongMessageSocket(socket)
        self.address = address
        self.topologyServer = topologyServer
        self.requestId = 0
        
    def get_request_id(self):
        self.requestId += 1
        return  self.requestId
        
    def run(self):
        try:
            jsonMessage = 'not null'
            reqFactory = RequestFactory()
        
            while jsonMessage != '':
                jsonMessage = self.socket.recv()
            
                request = reqFactory.decodeJson(jsonMessage)
                if request.action == request.ACTION.GET_TOPOLOGY:
                    print '\tMessage request(getTopology) received from client', self.address
                    self.request_get_topology(request)
                
                elif request.action == request.ACTION.GET_COMPLETE_GROUP:
                    print '\tMessage request(getCompleteGroup) received from client', self.address
                    self.request_get_group(request=request, complete=True)
                
                elif request.action == request.ACTION.GET_GROUP:
                    print '\tMessage request(getGroup) received from client', self.address
                    self.request_get_group(request=request, complete=False)
                
                elif request.action == request.ACTION.REGISTER_FOR_EVENTS:
                    print '\tMessage request(registerForEvents) received from client', self.address
                    self.request_register_for_events(request)
                
                elif request.action == request.ACTION.WAIT_START:
                    print '\tMessage request(waitStart) received from client', self.address
                    self.request_wait_start(request)
                
                elif request.action == request.ACTION.START:
                    print '\tMessage request(start) received from client', self.address
                    self.request_start(request)
                    
                elif request.action == request.ACTION.UPDATE_TOPOLOGY:
                    print '\tMessage request(updateTopology) received from client', self.address
                    self.request_update_topology(request)
                
                elif request.action == request.ACTION.ENTRY_GROUP:
                    print '\tMessage request(entryGroup) received from client', self.address
                    self.request_entry_group(request)
                    
                elif request.action == request.ACTION.EXIT_GROUP:
                    print '\tMessage request(entryGroup) received from client', self.address
                    self.request_exit_group(request)
                    
                elif request.action == request.ACTION.CHANGE_SOURCE:
                    print '\tMessage request(changeSource) received from client', self.address
                    self.request_change_source(request)
                
                elif request.action == request.ACTION.ENTRY_EVENT:
                    print '\tMessage request(entryEvent) received from client', self.address
                    self.request_entry_event(request)
                    
                elif request.action == request.ACTION.EXIT_EVENT:
                    print '\tMessage request(exitEvent) received from client', self.address
                    self.request_exit_event(request)
                    
                elif request.action == request.ACTION.SOURCE_EVENT:
                    print '\tMessage request(sourceEvent) received from client', self.address
                    self.request_source_event(request)
                
                else:
                    print '\tInvalid Request type received from client', self.address
                    return 'none'
                
        except RuntimeError as inst:
            print 'RuntimeError has occurred:', inst
        
        self.socket.close()
        print 'Connection with client', self.address, 'closed.'
        self.topologyServer.removeHandler(self)
    
    def request_get_topology(self, request):
        topology = self.topologyServer.getTopology()
        jsonMessage = topology.toJson()
        self.socket.send(jsonMessage)
        print '\tMessage topology sent to client', self.address
    
    def request_get_group(self, request, complete=False):
        group = self.topologyServer.getMulticastGroup(complete)
        jsonMessage = group.toJson()
        self.socket.send(jsonMessage)
        print '\tMessage group sent to client', self.address
    
    def request_register_for_events(self, request):
        self.topologyServer.addEventListeners(self)
        
    def request_wait_start(self, request):
        self.topologyServer.addStartListeners(self)
        
    def request_start(self, request):
        self.topologyServer.notifyStart(request)
        
    def request_update_topology(self, request):
        self.topologyServer.updateTopology(request)
        
    def request_entry_group(self, request):
        self.topologyServer.addEventListeners(self)
        self.topologyServer.entryEvent(request)
    
    def request_exit_group(self, request):
        self.topologyServer.addEventListeners(self)
        self.topologyServer.exitEvent(request)
        
    def request_change_source(self, request):
        self.topologyServer.addEventListeners(self)
        self.topologyServer.changeSource(request)
        
    def request_entry_event(self, request):
        self.topologyServer.entryEvent(request)
    
    def request_exit_event(self, request):
        self.topologyServer.exitEvent(request)
    
    def request_source_event(self, request):
        self.topologyServer.changeSource(request)
        
        
    def notify_client(self, notification):
        jsonMessage = notification.toJson()
        self.socket.send(jsonMessage)
        if notification.__class__ == Request:
            print '\tMessage request(start) sent to client', self.address
        elif notification.__class__ == Event:
            print '\tMessage event sent to client', self.address