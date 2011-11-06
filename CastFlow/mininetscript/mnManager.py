"""mininet Custom script

@author: arthurgodoy
"""
from mnCustomTopology import *

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('localhost', 8887)
    print 'Trying to connect on server', address
    s.connect(address)
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
    print 'Parsing Topology Message ok.'
        
    #Start new thread that create a custom topology from routers, hosts and links received and care about the client group
    thread = mnCustomGroup(topology,clientSocket)
    thread.start()
