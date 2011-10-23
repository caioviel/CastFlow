'''
Created on Oct 20, 2011

@author: caioviel
'''

from topologyserver.TopologyServer import *

if __name__ == '__main__':
        server = TopologyServer('brite1.brite')
        server.startListen()
        
        
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect( ('localhost', 8887) )
    
    clientSocket = LongMessageSocket(s)
    
    request = Request()
    request.id = 0
    request.action = request.ACTION.GET_TOPOLOGY
    jsonMessage = request.toJson()
    
    clientSocket.send(jsonMessage)
    jsonTopology = clientSocket.recv()
    print jsonTopology
    
    clientSocket.close()
        
        
    