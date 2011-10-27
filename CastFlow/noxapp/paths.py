'''
Created on Oct 26, 2011

@author: tiagopomponet
'''
from commum.Model import Request, GroupFactory
from commum.util import *
from noxapp.MST import MST

class Paths:

    def __init__(self):
        self.t = MST()
        self.topology = self.t.getRemoteMST()
        self.topology = self.dupPaths()

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('localhost', 8887)
        s.connect( address )
        clientSocket = LongMessageSocket(s)
        return clientSocket
        
    def getGroup(self):
        request = Request()
        request.id = 3
        request.action = request.ACTION.GET_GROUP
        jsonMessage = request.toJson()
        
        clientSocket = self.connect()
        
        clientSocket.send(jsonMessage)
        jsonTopology = clientSocket.recv()
        clientSocket.close()
        self.group = GroupFactory().decodeJson(jsonTopology)

        return self.group
        
    def parseGroup(self):
        paths = []
        self.source = self.group.source
        for h in self.group.hosts:
            opath = []
            opath2 = self.getPath(self.source, h.id, opath)
            print opath2
            paths.append(opath2)
        return paths
    
    def belong(self, element, vlist):
        for i in vlist:
            if i == element:
                return 1
        return 0
    
    def getPath(self, source, destiny, mpath):
        mpath.append(source)
        for tuple in self.topology:
            node1,node2,peso = tuple
            if node1 == str(source):
                if node2 == str(destiny):
                    mpath.append(int(node2))
                    return mpath
                
                srctemp = int(node2)
                if self.belong(srctemp, mpath) == 0:
                    mpath = self.getPath(srctemp, destiny, mpath)
                    last = mpath[len(mpath)-1]
                    if last == destiny:
                        break
                    else:
                        mpath.pop()
        return mpath
    
    def dupPaths(self):
        tmp = []
        tmp.extend(self.topology)
        for tuple in self.topology:
            node1,node2,peso = tuple
            t = node2, node1, peso
            tmp.append(t)
        return tmp
    
    def getPaths(self):
        self.group = self.getGroup()
        return self.parseGroup()