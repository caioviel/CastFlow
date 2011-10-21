'''
Created on Oct 20, 2011

@author: caioviel
'''

from topologyserver.TopologyManager import *
import socket

if __name__ == '__main__':
    topMng = TopologyManager()
    topMng.importTopologyFromBrite('brite1.brite')
    
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(8888)
    
    serverSocket.listen(5)
    while True:
        clientSocket, address = serverSocket.accept()
        ct = client_thread(clientSocket)
    
    
    
    
    
    
    
    