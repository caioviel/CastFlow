import socket

from commum.Model import *
from commum.util import *

if __name__ == '__main__':
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
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    jsonTopology = clientSocket.recv()
    print 'Message received:', jsonTopology
    topology = TopologyFactory().decodeJson(jsonTopology)
    print 'Parsing Topolgoy Message ok.'
    
    #Sending a Request Topology Update
    topology.hosts[0].mac = 'ca:fe:ca:fe:ca:fe'
    topology.hosts[0].ip = '192.168.10.65'
    print 'Set the ip and mac address: ', topology.hosts[1]
    request.id = 3
    request.action = request.ACTION.UPDATE_TOPOLOGY
    request.topology = topology
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    clientSocket.send(jsonMessage)
    
    #Sending Complete Group Request
    
    request.id = 4
    request.action = request.ACTION.GET_COMPLETE_GROUP
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    jsonTopology = clientSocket.recv()
    print 'Message received:', jsonTopology
    topology = GroupFactory().decodeJson(jsonTopology)
    print 'Parsing Group Message ok.'
    
    #Sending Group Request
    
    request.id = 5
    request.action = request.ACTION.GET_GROUP
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    jsonTopology = clientSocket.recv()
    print 'Message received:', jsonTopology
    topology = GroupFactory().decodeJson(jsonTopology)
    print 'Parsing Group Message ok.'
    
    #Sending Wait Start Request
    
    request.id = 6
    request.action = request.ACTION.WAIT_START
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    
    #Sending Start Request
    
    request.id = 7
    request.action = request.ACTION.START
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    
    #Waiting for Start Request
    
    print 'Waiting for start...'
    jsonTopology = clientSocket.recv()
    print 'Message received:', jsonTopology
    topology = RequestFactory().decodeJson(jsonTopology)
    print 'Parsing Request Start Message ok.'
    
    #Sending Register for Events Request
    
    request.id = 8
    request.action = request.ACTION.REGISTER_FOR_EVENTS
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    
    #Waiting for Events Messages
    print 'Waiting for events...'
    while True:
        jsonTopology = clientSocket.recv()
        print 'Message received:', jsonTopology
        event = EventFactory().decodeJson(jsonTopology)
        print 'Parsing Event Message ok.'
    
    clientSocket.close()
    print 'Connection closed.'