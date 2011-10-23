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
    
    #Sending Complete Group Request
    
    request.id = 2
    request.action = request.ACTION.GET_COMPLETE_GROUP
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    jsonTopology = clientSocket.recv()
    print 'Message received:', jsonTopology
    topology = GroupFactory().decodeJson(jsonTopology)
    print 'Parsing Group Message ok.'
    
    #Sending Group Request
    
    request.id = 3
    request.action = request.ACTION.GET_GROUP
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    jsonTopology = clientSocket.recv()
    print 'Message received:', jsonTopology
    topology = GroupFactory().decodeJson(jsonTopology)
    print 'Parsing Group Message ok.'
    
    #Sending Wait Start Request
    
    request.id = 4
    request.action = request.ACTION.WAIT_START
    jsonMessage = request.toJson()
    print 'Sending message: ', jsonMessage
    
    clientSocket.send(jsonMessage)
    
    #Sending Start Request
    
    request.id = 5
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
    
    clientSocket.close()
    print 'Connection closed.'