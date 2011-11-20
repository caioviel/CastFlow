'''
Created on Oct 20, 2011

@author: caioviel
'''
import json

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Router:
    '''
    classdocs
    '''
    def __init__(self):
        self.allports = []
        self.links = []
        self.id = -1
        self.distanceFromSource = -1
        
    def addPort(self, nodeid, linkid):
        self.allports.append(nodeid)
        self.links.append(linkid)
            
    def getNodeByPort(self, port):
        if len(self.allports) > (port -1):
            return self.allports[port-1]
        else:
            print 'Trying to access a inexistent port.'
            
    def getPortByNode(self, nodeid):
        for i in range( len(self.allports) ):
            if self.allports[i] == nodeid:
                return i+1
        print 'Trying to access a inexistent port.'
        
        
    def getLinkByPort(self, linkid):
        if len(self.links) > (linkid -1):
            return self.links[linkid-1]
        else:
            print 'Trying to access a inexistent port.'
            
    def getLinkByNode(self, nodeid):
        for i in range( len(self.allports) ):
            if self.allports[i] == nodeid:
                return self.links[i]
        print 'Trying to access a inexistent port.'
            
            
    def internal_toJson(self):
        ports = []
        for i in range(len(self.allports)):
            ports.append( {'port' : {'node' :  self.allports[i], 'link' : self.links[i] } } )
            
        return {'router' : {'id' : self.id, 'ports' : ports} }
                
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
    def __str__(self):
        return self.toJson();

class RouterFactory:
    def createRouter(self, myId, ports):
        r = Router()
        r.id = myId
        r.ports = ports
        return r
    
    def decodeJson(self, jsonStr):
        objs = json.loads(jsonStr)
        return self.internal_decodeJson(objs)
    
    def internal_decodeJson(self, objs):
        router = Router()
        router.id = objs['router']['id']
        ports =  objs['router']['ports']
        for port in ports:
            router.allports.append(port['port']['node'])
            router.links.append(port['port']['link'])
        return router
    
class Link:
    def __init__(self):
        self.id = -1
        self.weight = -1

    def internal_toJson(self):
        return {'link' : 
                {'id' : self.id, 'node1' : self.node1, 
                 'node2' : self.node2, 'weight' : self.weight} }
        
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
    def __str__(self):
        return self.toJson();
        
        
class LinkFactory:
    def createLink(self, myId, node1, node2):
        l = Link()
        l.id = myId
        l.node1 = node1
        l.node2 = node2
        return l
    
    def internal_decodeJson(self, objs):
        link = Link()
        link.id = objs['link']['id']
        link.node1 = objs['link']['node1']
        link.node2 = objs['link']['node2']
        link.weight = objs['link']['weight']
        return link
    
    def decodeJson(self, jsonStr):
        objs = json.loads(jsonStr)
        return self.internal_decodeJson(objs)
    

class Host:
    def __init__(self):
        self.id = -1
        self.link = -1
        self.ip = "0.0.0.0"
        self.mac = "00:00:00:00:00:00"
        self.distanceFromSource = -1
        
    def internal_toJson(self):
        return {'host' : 
                           {'id' : self.id, 'router' : self.router, 'link' : self.link, 'ip' : self.ip, 'mac' : self.mac} } 
    
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
    def addressedById(self):
        self.ip = '10.0.0.' + str(self.id)
        hex_id = hex(self.id)
        hex_id = hex_id[2:]
        if len(hex_id) == 1:
            hex_id = '0' + hex_id
        self.mac = '00:00:00:00:00:' + hex_id
    
    def __str__(self):
        return self.toJson();
    
class HostFactory:
    def createHost(self, myId, router):
        h = Host()
        h.id = myId
        h.router = router
        return h
    
    def internal_decodeJson(self, objs):
        host = Host()
        host.id = objs['host']['id']
        host.router = objs['host']['router']
        host.link = objs['host']['link']
        host.ip = objs['host']['ip']
        host.mac = objs['host']['mac']
        return host
        
    def decodeJson(self, jsonStr):
        objs = json.loads(jsonStr)
        return self.internal_decodeJson(objs)
    
class Topology:

    def __init__(self):
        self.routers = []
        self.hosts = []
        self.links = []

    def internal_toJson(self):
        rts = []
        for r in self.routers:
            rts.append(r.internal_toJson())

        lks = []
        for l in self.links:
            lks.append(l.internal_toJson())

        hts = []
        for h in self.hosts:
            hts.append(h.internal_toJson())
            
        return {'topology' :
                            {'routers' : rts, 
                             'links' : lks, 
                             'hosts' : hts} }
        
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
    def isHost(self, nodeid):
        if nodeid > len(self.routers):
            return True
        else:
            return False
        
    def getHostById(self, hostid):
        return self.hosts[hostid - (len(self.routers) + 1)]
        
    def getRouterById(self, routerid):
        return self.routers[routerid - 1]
    
    def getLinkById(self, linkid):
        return self.links[linkid - 1]
        
class TopologyFactory:
    def internal_decodeJson(self, objs):
        hosts = []
        routers = []
        links = []
        
        factory = RouterFactory()
        array_list = objs['topology']['routers']
        for item in array_list:
            routers.append( factory.internal_decodeJson(item) ) 

        factory = LinkFactory()
        array_list = objs['topology']['links']
        for item in array_list:
            links.append(factory.internal_decodeJson(item))

        factory = HostFactory()
        array_list = objs['topology']['hosts']
        for item in array_list:
            hosts.append(factory.internal_decodeJson(item))

        t = Topology()
        t.routers = routers
        t.links = links
        t.hosts = hosts
        return t
    
    def decodeJson(self, jsonStr):
        objs = json.loads(jsonStr)
        return self.internal_decodeJson(objs)
    
class Group:
    def __init__(self, source=-1):
        self.hosts = []
        self.source = source
        pass    

    def internal_toJson(self):
        hts = []
        for h in self.hosts:
            hts.append(h.internal_toJson())
            
        return {'group' :
                            {'source' : self.source,
                             'hosts' : hts} }
        
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
class GroupFactory:
    def internal_decodeJson(self, objs):
        hosts = []

        factory = HostFactory()
        array_list = objs['group']['hosts']
        for item in array_list:
            hosts.append(factory.internal_decodeJson(item))

        g = Group()
        g.source = objs['group']['source']
        g.hosts = hosts
        return g
    
    def decodeJson(self, jsonStr):
        objs = json.loads(jsonStr)
        return self.internal_decodeJson(objs)
    
class Event:
    def __init__(self, myid=-1, mytype='entry'):
        self.id = myid
        self.type = mytype
        self.hosts = []
        self.source = -1
        pass

    def internal_toJson(self):
        hts = []
        for h in self.hosts:
            hts.append(h.internal_toJson())
            
        if self.type == 'changeSource':
            return {'event' :
                            {'id' : self.id, 'type' : self.type,
                             'source' : self.source} }
        else:
            return {'event' :
                            {'id' : self.id, 'type' : self.type,
                             'hosts' : hts} }
    
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
class EventFactory:
    def internal_decodeJson(self, objs):
        hosts = []

        e = Event()
        e.id = objs['event']['id']
        e.type = objs['event']['type']
        if e.type == 'changeSource':
            e.source = objs['event']['source']
        else: 
            factory = HostFactory()
            array_list = objs['event']['hosts']
            for item in array_list:
                hosts.append(factory.internal_decodeJson(item))
            e.hosts = hosts
        return e
    
    def decodeJson(self, jsonStr):
        objs = json.loads(jsonStr)
        return self.internal_decodeJson(objs)
    
class Request:
    ACTION = enum('GET_TOPOLOGY', 'GET_COMPLETE_GROUP', 
                  'GET_GROUP', 'REGISTER_FOR_EVENTS', 
                  'WAIT_START', 'START', 'NONE', 
                  'UPDATE_TOPOLOGY', 'ENTRY_GROUP', 
                  'EXIT_GROUP', 'CHANGE_SOURCE',
                  'ENTRY_EVENT', 'EXIT_EVENT',
                  'SOURCE_EVENT')
    
    def __init__(self, myid = -1, action = ACTION.NONE):
        self.id = myid
        self.action = action
        self.topology = None
        self.hosts = []
        self.source = -1
        
    def internal_toJson(self):
        if self.action == self.ACTION.UPDATE_TOPOLOGY:
            return {'request' : {'id' : self.id, 'action' : self.ACTION_to_string(self.action), 
                                 'topology' : self.topology.internal_toJson() } }
        elif self.action == self.ACTION.ENTRY_GROUP or self.action == self.ACTION.EXIT_GROUP:
            return {'request' : {'id' : self.id, 'action' : self.ACTION_to_string(self.action), 
                                 'hosts' : self.hosts } }
        elif self.action == self.ACTION.CHANGE_SOURCE:
            return {'request' : {'id' : self.id, 'action' : self.ACTION_to_string(self.action), 
                                 'source' : self.source } }
        else:
            return {'request' : {'id' : self.id, 'action' : self.ACTION_to_string(self.action)} }

    
        
    def ACTION_to_string(self, action):
        if action == self.ACTION.GET_TOPOLOGY:
            return 'getTopology'
        elif action == self.ACTION.GET_COMPLETE_GROUP:
            return 'getCompleteGroup'
        elif action == self.ACTION.GET_GROUP:
            return 'getGroup'
        elif action == self.ACTION.REGISTER_FOR_EVENTS:
            return 'registerForEvents'
        elif action == self.ACTION.WAIT_START:
            return 'waitStart'
        elif action == self.ACTION.START:
            return 'start'
        elif action == self.ACTION.UPDATE_TOPOLOGY:
            return 'updateTopology'
        elif action == self.ACTION.EXIT_GROUP:
            return 'exitGroup'
        elif action == self.ACTION.ENTRY_GROUP:
            return 'entryGroup'
        elif action == self.ACTION.CHANGE_SOURCE:
            return 'changeSource'
        elif action == self.ACTION.ENTRY_EVENT:
            return 'entryEvent'
        elif action == self.ACTION.EXIT_EVENT:
            return 'exitEvent'
        elif action == self.ACTION.SOURCE_EVENT:
            return 'sourceEvent'
        else:
            return 'none'
    
    def string_to_ACTION(self, actionStr):
        if actionStr == 'getTopology':
            return self.ACTION.GET_TOPOLOGY
        elif actionStr == 'getCompleteGroup':
            return self.ACTION.GET_COMPLETE_GROUP
        elif actionStr == 'getGroup':
            return self.ACTION.GET_GROUP
        elif actionStr == 'registerForEvents':
            return self.ACTION.REGISTER_FOR_EVENTS
        elif actionStr == 'waitStart':
            return self.ACTION.WAIT_START
        elif actionStr == 'start':
            return self.ACTION.START
        elif actionStr == 'updateTopology':
            return self.ACTION.UPDATE_TOPOLOGY
        elif actionStr == 'exitGroup':
            return self.ACTION.EXIT_GROUP
        elif actionStr == 'entryGroup':
            return self.ACTION.ENTRY_GROUP
        elif actionStr == 'changeSource':
            return self.ACTION.CHANGE_SOURCE
        elif actionStr == 'entryEvent':
            return self.ACTION.ENTRY_EVENT
        elif actionStr == 'exitEvent':
            return self.ACTION.EXIT_EVENT
        elif actionStr == 'sourceEvent':
            return self.ACTION.SOURCE_EVENT
        else:
            return self.ACTION.NONE
        
    def toJson(self):
        return json.dumps(self.internal_toJson())
    
class RequestFactory:
    def internal_decodeJson(self, objs):
        request = Request()
        request.id = objs['request']['id']
        request.action = request.string_to_ACTION( objs['request']['action'] )
        if request.action == request.ACTION.UPDATE_TOPOLOGY:
            request.topology = TopologyFactory().internal_decodeJson(objs['request']['topology'])
        elif request.action == request.ACTION.ENTRY_GROUP or request.action == request.ACTION.EXIT_GROUP:
            request.hosts = objs['request']['hosts']
        elif request.action == request.ACTION.CHANGE_SOURCE:
            request.source = objs['request']['source']
        return request
    
    def decodeJson(self, jsonStr):
        print jsonStr
        objs = json.loads(jsonStr)
        #print objs
        return self.internal_decodeJson(objs)