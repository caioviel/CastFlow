'''
Created on Oct 26, 2011

@author: tiagopomponet    
'''

    def __str__(self):
        return self.toJson()

class Paths:
    def __init__(self):
        self.t = MST()
        self.topology = self.t.getRemoteMST()
        self.topology = self.dupPaths()
        pass

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
            paths.append(self.getPath(self.source, h.id, opath))
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
        for mytuple in self.topology:
            node1,node2,peso = mytuple
            t = node2, node1, peso
            tmp.append(t)
        return tmp
    
    def getPaths(self):
        self.group = self.getGroup()
        return self.parseGroup()
    
    def prepareInstall(self, paths):
        s = []
        for p in paths:
            for i in range(len(p)-1):
                pair = [p[i],p[i+1]]
                if pair not in s:
                    s.append(pair)
                    
        s.sort()
        print s
        
        all_installs = []
        while len(s) > 0:
            install = s.pop(0)
            if len(s) > 0:
                while install[0] == s[0][0]:
                    temp = s.pop(0)
                    install.append(temp[1])
                
            all_installs.append(install)
            
        return all_installs
    
    def getTopology(self):
        return self.topology
    
    
    def getInstalantions(self):
        paths = self.getPaths()
        print paths
        
        s = []
        for p in paths:
            for i in range(1, len(p)-1):
                pair = [p[i], p[i-1], p[i+1]]
                if pair not in s:
                    s.append(pair)
                    
        s.sort()
        print s
        
        cTopology = self.t.topology;
        
        all_installs = []
        while len(s) > 0:
            hope = s.pop(0)
            installPath = InstallPath()
            installPath.routerId = hope[0]
            router = cTopology.getRouterById(installPath.routerId)
            installPath.inputPort = router.getPortByNode(hope[1])
            
            nodeid = hope[2]
            if cTopology.isHost(nodeid):
                host = cTopology.getHostById(nodeid)
                installPath.needRewrite = True
                installPath.dst_ip = host.ip
                installPath.dst_mac = host.mac
            
            installPath.addOutputPort( router.getPortByNode(nodeid) )
            
            while len(s) > 0 and installPath.routerId == s[0][0]:
                temp = s.pop(0)
                    
                nodeid = temp[2]
                if cTopology.isHost(nodeid):
                    host = cTopology.getHostById(nodeid)
                    installPath.needRewrite = True
                    installPath.dst_ip = host.ip
                    installPath.dst_mac = host.mac
            
                installPath.addOutputPort( router.getPortByNode(nodeid) )
                
            all_installs.append(installPath)
            
        return all_installs
            
''''p = Paths()
installs = p.getInstalantions()

for i in installs:
    print i'''



