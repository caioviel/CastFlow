'''
Created on Oct 23, 2011

@author: caioviel
'''

import threading

class AsynchronousNotifier(threading.Thread):
    def __init__(self, toNotify, notification):
        threading.Thread.__init__(self)
        self.toNotify = toNotify
        self.notification = notification
        
    def doNotify(self):
        threading.Thread.start(self)
    
    def run(self):
        self.toNotify.notify_client(self.notification)

class InternalInterface:
    '''
    classdocs
    '''
    def getTopology(self):
        pass
    
    def getMulticastGroup(self, complete=False):
        pass
    
    def addEventListeners(self, handler):
        pass
            
    
    def addStartListeners(self, handler):
        pass
    
    def removeHandler(self, handler):
        pass
    
    def notifyStart(self, request):
        pass
            
    def notifyEvent(self, event):
        pass