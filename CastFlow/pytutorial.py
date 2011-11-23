# Tutorial Controller
# Starts as a hub, and your job is to turn this into a learning switch.

import logging

from nox.lib.core import *
import nox.lib.openflow as openflow
from nox.lib.packet.ethernet import ethernet
from nox.lib.packet.packet_utils import mac_to_str, mac_to_int

from commum.Model import *
from commum.util import *
from noxapp_exp.InstallationManager import *

log = logging.getLogger('nox.coreapps.tutorial.pytutorial')


class pytutorial(Component):

    def install_routes(self):
        #print '\n\n\n\n\n'        
        print '************ INSTALLING ROUTES ****************'
        installs = self.im.installs_to_do

        for install in installs:
            #print '\tInstalling: ', install
            attrs = {}
            attrs[core.IN_PORT] = install.inputPort
            actions = []
            if install.needRewrite == True :
                actions.append( [openflow.OFPAT_SET_DL_SRC, "ca:fe:ca:fe:ca:fe"] )
                actions.append( [openflow.OFPAT_SET_NW_SRC, "10.0.2.254"] )
                actions.append ([openflow.OFPAT_SET_DL_DST, str(install.dst_mac) ] )
                actions.append ([openflow.OFPAT_SET_NW_DST, str(install.dst_ip) ] )

            for port in install.outputPorts:
                actions.append( [openflow.OFPAT_OUTPUT, [0, port] ] )
                
            self.install_datapath_flow(install.routerId, attrs, 3600, 3600, actions, None, openflow.OFP_DEFAULT_PRIORITY, install.inputPort, None)
            
        print '********** REMOVING OBSOLUTE ROUTES ***********'
        removes = self.im.installs_to_remove
        for install in removes:
            #print 'Removing: ', install
            attrs = {}
            attrs[core.IN_PORT] = install.inputPort
            self.delete_datapath_flow(install.routerId, attrs)
            
        print '********** FINISHED INSTALLATION ***********'

    def __init__(self, ctxt):
        Component.__init__(self, ctxt)
        # Use this table to store MAC addresses in the format of your choice;
        # Functions already imported, including mac_to_str, and mac_to_int,
        # should prove useful for converting the byte array provided by NOX
        # for packet MAC destination fields.
        # This table is initialized to empty when your module starts up.
        # self.mac_to_port = {} # key: MAC addr; value: port
        self.im = None

    def learn_and_forward(self, dpid, inport, packet, buf, bufid):
        """Learn MAC src port mapping, then flood or send unicast."""
        pass

    def packet_in_callback(self, dpid, inport, reason, len, bufid, packet):
        """Packet-in handler""" 
        if not packet.parsed:
            log.debug('Ignoring incomplete packet')
        else:
            print 'Packet-in no router', dpid, '--Fonte:', mac_to_str(packet.src), '--Destino:', mac_to_str(packet.dst)
            print 'In-Port:', inport

        if self.im == None:
            self.im = InstallationManager()
            self.im.nox = self
            #self.im.samples_number = 10
            self.im.collect_begin_installs()
            self.install_routes()
            self.im.collect_end_installs()
            self.im.start()

        return CONTINUE

    def install(self):
        self.register_for_packet_in(self.packet_in_callback)
    
    def getInterface(self):
        return str(pytutorial)

def getFactory():
    class Factory:
        def instance(self, ctxt):
            return pytutorial(ctxt)

    return Factory()