'''
Created on Oct 23, 2011

@author: caioviel
'''

import socket

class LongMessageSocket:
    '''
    classdocs
    '''

    def __init__(self, mySocket):
        '''
        Constructor
        '''
        self.socket = mySocket
        
    def send(self, message):
        totalsent = 0
        fullMessage = '<' + str( len(message) ) + '>' + message
        fullMessageLenght = len(fullMessage)
        while totalsent < fullMessageLenght:
            sent = self.socket.send(fullMessage[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
    
    def recv(self):
        firstPacket = self.socket.recv(4096)
        if firstPacket == '':
            raise RuntimeError("socket connection broken")
        message = ''
        head, sep, tail = firstPacket.partition('>')
        originalSize = int(head[1:])
        message += tail
        
        while len(message) < originalSize:
            chunk = self.socket.recv(4096)
            if chunk == '':
                raise RuntimeError("socket connection broken")
            message += chunk
            
        return message
        
    def close(self):
        self.socket.close()
        