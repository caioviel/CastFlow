'''
Created on Nov 12, 2011

@author: caioviel
'''

from commum.Model import *
from commum.util import *
from noxapp_exp.MSTParser import MSTParser

import threading

class InstallPath:
    def __init__(self):
        self.routerId = -1
        self.inputPort = -1
        self.outputPorts = []
        self.needRewrite = False
        self.dst_mac = ''
        self.dst_ip = ''
        
    def addOutputPort(self, portnumber):
        self.outputPorts.append(portnumber)
        
    def toJson(self):
        if self.needRewrite:
            return json.dumps({'InstallPath' : {'routerId' : self.routerId,
                                 'inputPort' : self.inputPort,
                                 'outputPorts' : self.outputPorts,
                                 'rewrite' : str(self.needRewrite),
                                 'dst_mac' : self.dst_mac,
                                 'dst_ip' : self.dst_ip}})
        else:
            return json.dumps({'InstallPath' : {'routerId' : self.routerId,
                                 'inputPort' : self.inputPort,
                                 'outputPorts' : self.outputPorts}})
        
    def __str__(self):
        return self.toJson()
    

class InstallationManager(threading.Thread):
    def get_installs_to_remove(self):
        return self.installs_to_remove
    
    def get_installs_to_do(self):
        return self.installs_to_do
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.__connect__()
        self.req_number = 0
        
        #Get the Topology from Topology Server
        self.__get_topology__()
        
        #Create the minimum spanning tree from the topology graph        
        complete_group = self.__get_complete_group__()
        self.paths_by_source = {}
        
        #Copy the array because it will be changed during the calc path's process
        temp_hosts = complete_group.hosts[0:]
            
        for host in complete_group.hosts:
            mst = MSTParser(self.topology, host).get_mst( algorithm = 'prim' )
            mst = self.__duplicate_paths__(mst)
            self.paths_by_source[host.id] = self.__calc_paths_by_source__(mst, host, temp_hosts)
        
        #Get the actual Multicast Group from the Topology Server
        self.__get_group__()
        self.path_to_host = self.paths_by_source[self.current_source]
        
        #Calculate the initial installation hops
        self.__calcultate_initial_hops__()
        
        #Generate the initial openflow installations list
        self.current_installs = self.__generate_installs__()
        self.installs_by_router = {}
        for install in self.current_installs:
            self.installs_by_router[install.routerId] = install
        
        #Set the begin configurations status
        self.installs_to_remove = []
        self.installs_to_do = self.current_installs
        
        self.has_installation = True
        
        #Start listening to events
        self.start()
        self.nox = None
        
    def __connect__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('localhost', 8887)
        s.connect( address )
        clientSocket = LongMessageSocket(s)
        self.socket = clientSocket
        
    def __belong__(self, element, vlist):
        for i in vlist:
            if i == element:
                return 1
        return 0
        
    def __next_req_number__(self):
        self.req_number = self.req_number +1
        return self.req_number
        
    def __get_topology__(self):
        request = Request()
        request.id = self.__next_req_number__()
        request.action = request.ACTION.GET_TOPOLOGY
        jsonMessage = request.toJson()
        
        self.socket.send( jsonMessage )
        jsonTopology = self.socket.recv()
        self.topology = TopologyFactory().decodeJson( jsonTopology )
        
    def __get_path__(self, source, destiny, mpath, mst):
        mpath.append(source)
        for t in mst:
            node1, node2, weight = t
            if node1 == str(source):
                if node2 == str(destiny):
                    mpath.append(int(node2))
                    return mpath
                
                srctemp = int(node2)
                if self.__belong__(srctemp, mpath) == 0:
                    mpath = self.__get_path__(srctemp, destiny, mpath, mst)
                    last = mpath[len(mpath)-1]
                    if last == destiny:
                        break
                    else:
                        mpath.pop()
        return mpath
    
    def get_path(self, nodeid):
        return self.path_to_host[nodeid]
    
    def get_all_paths(self):
        paths = []
        for path in self.path_to_host.values():
            paths.append(path)
        
        return paths
    
    def __get_complete_group__(self):
        request = Request()
        request.id = self.__next_req_number__()
        request.action = request.ACTION.GET_COMPLETE_GROUP
        jsonMessage = request.toJson()
        
        self.socket.send( jsonMessage )
        jsonGroup = self.socket.recv()
        
        group = GroupFactory().decodeJson( jsonGroup )
        return group;
        
        
    def __calc_paths_by_source__(self, mst, multicast_source, hosts):
        path_to_host = {}
        hosts.remove(multicast_source)
        for host in hosts:
            if host.id != multicast_source.id:
                opath = []
                path_to_host[host.id] = self.__get_path__(multicast_source.id, host.id, opath, mst)
        
        hosts.append(multicast_source)
        return path_to_host
        
    def __get_group__(self):
        request = Request()
        request.id = self.__next_req_number__()
        request.action = request.ACTION.GET_GROUP
        jsonMessage = request.toJson()
        
        self.socket.send( jsonMessage )
        jsonGroup = self.socket.recv()
        group = GroupFactory().decodeJson( jsonGroup )
        self.current_source = group.source
        self.active_hosts = []
        for host in group.hosts:
            self.active_hosts.append(host.id)
        
    def __duplicate_paths__(self, mst):
        tmp = []
        tmp.extend(mst)
        for mytuple in mst:
            node1,node2,peso = mytuple
            t = node2, node1, peso
            tmp.append(t)
        return tmp
        
    def __calcultate_initial_hops__(self):
        #Get the paths to all the active hosts
        paths = []
        for host in self.active_hosts:
            paths.append(self.path_to_host[host])
            
        #Generate the list of point-to-point installations
        self.hops = self.__calcule_hops__(paths)
        self.hops.sort()
        
    def __calcule_hops__(self, paths):
        hops = []
        for path in paths:
            for i in range(1, len(path)-1):
                # (NODEID, PREVIOUS_NODE, NEXT_NODE)
                hop = [path[i], path[i-1], path[i+1]]
                if hop not in hops:
                    hops.append(hop)
                    
        return hops
        
    def __generate_installs__(self):
        topo = self.topology;
        
        # Copy the self.hops to the local variable hops
        # It's need because we will modify the variable in the process
        hops = self.hops[0:]
        
        all_installs = []
        while len(hops) > 0:
            hop = hops.pop(0)
            installPath = InstallPath()
            installPath.routerId = hop[0]
            router = topo.getRouterById(installPath.routerId)
            installPath.inputPort = router.getPortByNode(hop[1])
            
            nodeid = hop[2]
            if topo.isHost(nodeid):
                host = topo.getHostById(nodeid)
                installPath.needRewrite = True
                installPath.dst_ip = host.ip
                installPath.dst_mac = host.mac
            
            installPath.addOutputPort( router.getPortByNode(nodeid) )
            
            while len(hops) > 0 and installPath.routerId == hops[0][0]:
                temp = hops.pop(0)
                    
                nodeid = temp[2]
                if topo.isHost(nodeid):
                    host = topo.getHostById(nodeid)
                    installPath.needRewrite = True
                    installPath.dst_ip = host.ip
                    installPath.dst_mac = host.mac
            
                installPath.addOutputPort( router.getPortByNode(nodeid) )
                
            all_installs.append(installPath)
            
        return all_installs
    
    def run(self):
        #Send a Request Start to the server
        request = Request()
        request.id = self.__next_req_number__()
        request.action = request.ACTION.START
        jsonMessage = request.toJson()
        self.socket.send( jsonMessage )
        
        #Send a Request Register for Events
        request = Request()
        request.id = self.__next_req_number__()
        request.action = request.ACTION.REGISTER_FOR_EVENTS
        jsonMessage = request.toJson()
        self.socket.send( jsonMessage )
        
        while True:
            jsonEvent = self.socket.recv()
            event = EventFactory().decodeJson( jsonEvent )
            if event.type == "entry":
                print 'Entry Event received.'
                self.entry_event(event)
            elif event.type == "exit":
                print 'Exit Event received.'
                self.exit_event(event)
            else:
                print 'Invalid event received.'
                continue
            
            self.has_installation = True
            if self.nox != None:
                self.nox.install_routes()
            else:
                print '\n\nInstalls to do:'
                for install in self.get_installs_to_do():
                    print '\t', install
        
                print '\n\nInstalls to remove:'
                for install in self.get_installs_to_remove():
                    print '\t', install
                
            
    def entry_event(self, event):
        new_paths = []
        for host in event.hosts:
            new_paths.append( self.path_to_host[host.id])
            self.active_hosts.append(host.id)
            
        new_hops = self.__calcule_hops__(new_paths)
        has_changes = False
        for hop in new_hops:
            if hop not in self.hops:
                has_changes = True
                self.hops.append(hop)
        
        if not has_changes:
            # Nothing change at all.
            return
        
        self.hops.sort()
        
        new_installs = self.__generate_installs__()
        self.installs_to_do = []
        for install in new_installs:
            old_install = self.installs_by_router.get(install.routerId)
            if old_install == None:
                #There wasn't a installation in this router
                self.installs_by_router[install.routerId] = install
                self.installs_to_do.append(install)
            else:
                #There was a previous installation in this router
                if (old_install.outputPorts == install.outputPorts 
                        and old_install.inputPort == install.inputPort):
                    #The installation is the same, just ignore.
                    pass
                else:
                    #The installation is different!
                    #self.installs_to_remove.append(old_install) #TODO: Verify if it's realy necessary
                    self.installs_to_do.append(install)
                    self.installs_by_router[install.routerId] = install
        
    def exit_event(self, event):
        for host in event.hosts:
            self.active_hosts.remove(host.id)
            
        paths = []
        for host in self.active_hosts:
            paths.append(self.path_to_host[host])
            
        self.hops = self.__calcule_hops__(paths)
        self.hops.sort()
        
        new_installs = self.__generate_installs__()
        self.installs_to_do = []
        self.installs_to_remove = []
        keep_routers = []
        for install in new_installs:
            old_install = self.installs_by_router.get(install.routerId)
            keep_routers.append(install.routerId)
            if old_install == None:
                #There wasn't a installation in this router
                self.installs_by_router[install.routerId] = install
                self.installs_to_do.append(install)
            else:
                #There was a previous installation in this router
                if (old_install.outputPorts == install.outputPorts 
                        and old_install.inputPort == install.inputPort):
                    #The installation is the same, just ignore.
                    pass
                else:
                    #The installation is different!
                    #self.installs_to_remove.append(old_install) #TODO: Verify if it's realy necessary
                    self.installs_to_do.append(install)
                    self.installs_by_router[install.routerId] = install
                    
        for routerId in self.installs_by_router.keys():
            if routerId not in keep_routers:
                self.installs_to_remove.append( self.installs_by_router.pop(routerId) )
                    
        
        
if __name__ == '__main__':
    im = InstallationManager()
    allpaths = im.get_all_paths()
    print 'Total Paths: ', len(allpaths)
    for path in allpaths:
        print path
        
    print '\n'
    
    print 'Active Hosts:', im.active_hosts
    
    print 'Point to Point Installations: ', im.hops
    
    print '\n\nInstalls to do:'
    for install in im.get_installs_to_do():
        print '\t', install
        
    print '\n\nInstalls to remove:'
    for install in im.get_installs_to_remove():
        print '\t', install
        