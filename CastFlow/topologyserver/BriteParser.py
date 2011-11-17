'''
Created on Oct 20, 2011

@author: caioviel
'''

from commum.Model import Host, Link, Router, LinkFactory, HostFactory

class BriteParser:
    def __init__(self, filename, delta_id = 1):
        self.delta_id = delta_id
        self.links = []
        self.routers = []
        self.hosts = []
        self.filename = filename
    
    def doParse(self):
        britefile = open(self.filename, 'r')
        britefile.readline()
        britefile.readline()
        britefile.readline()
        britefile.read(8)
        
        self.__parseRouters__(britefile)
        
        britefile.readline()
        britefile.readline()
        britefile.read(8)
        self.__parseLinks__(britefile)
        
        self.__generateHosts__()
        
        self.__completeRouters__()

            
    def __parseRouters__(self, britefile):
        line = britefile.readline()
        indexFinal = line.find(')')
        nRouters = line[:indexFinal]
        nRouters = int(nRouters)
        count = 0
        while count < nRouters:
            line = britefile.readline()
            router = Router()
            index = line.find('\t')
            routerid = (count+1) - self.delta_id
            router.id = routerid + self.delta_id
            self.routers.append( router )
            count += 1
        
    def __parseLinks__(self, britefile):
        line = britefile.readline()
        indexFinal = line.find(')')
        nLinks = line[:indexFinal]
        nLinks = int(nLinks)

        count = 0
        while count < nLinks:
            line = britefile.readline()
            index = line.find('\t')
            linkId = int(line[:index]) + self.delta_id
            line = line[index+1:]
            index = line.find('\t')
            node1 = int(line[:index]) + self.delta_id
            line = line[index+1:]
            index = line.find('\t')
            node2 = int(line[:index]) + self. delta_id
            link = LinkFactory().createLink(linkId, node1, node2)
            self.links.append(link)
            count += + 1
    
    def __generateHosts__(self):
        nextHostId = self.routers[len(self.routers)-1].id +1
        nextLinkId = self.links[len(self.links)-1].id +1
        for router in self.routers:
            host = HostFactory().createHost(nextHostId, router.id)
            host.addressedById()
            self.hosts.append(host)
            link = LinkFactory().createLink(nextLinkId, router.id, host.id)
            self.links.append(link)
            host.link = link.id
            nextHostId += 1
            nextLinkId += 1
    
    def __completeRouters__(self):
        biggerRouter = self.routers[len(self.routers)-1].id
        for link in self.links:
            if link.node1 <= biggerRouter: #is a router
                self.routers[link.node1 - 1].addPort(link.node2, link.id)
            else: #is a host
                self.hosts[link.node1 - biggerRouter -1].router = link.node2
                
            if link.node2 <= biggerRouter: #is a router
                self.routers[link.node2 -1].addPort(link.node1, link.id)
            else: #is a host
                self.hosts[link.node2 - biggerRouter -1].router = link.node1
            

