#!/usr/bin/env python
'''
Created on Oct 20, 2011

@author: caioviel
'''

import sys
from topologyserver.TopologyServer import TopologyServer
from topologyserver.TopologyManager import TopologyManager

def help():
    print 'Usage: toposerv -f <FILE> [-g -s -t -i -o -I -O --id-delta]'
    print'\t--file, -f <FILE>\t\tSet the brite file what will be used to generate the topology.'
    print'\t--group, -g <N> [<M>]\t\tSet the multicast group total size (<N>) and'
    print                    '\t\t\t\t\t   and initial active hosts number (<M>).'
    print '\t--source, -s <SOURCE>\t\tSet the initial source of multicast group.'
    print '\t--time, -t <TIME>\t\tSet the time between multicast event\'s generation.'
    print '\t--in, -i <N>\t\t\tSet the number of hosts for entryGroup events.'
    print '\t--out, -o <N>\t\t\tSet the number of hosts for exitGroup events.'
    print '\t--IN, -I <N>\t\t\tSet the parameter for Poisson distribution for entryGroup events.'
    print '\t--OUT, -O <N>\t\t\tSet the parameter for Poisson distribution for exitGroup events.'
    print '\t--delta, -d <N>\t\tSet the delta of routers/links ids parsed form brite files.'
    

groupSize = 0
groupInitialSize = 0
source = 0
hasEvent = False
eventTime = 40
entryPoisson = False
entryNumber = 1
exitPoisson = False
exitNumber = 1
delta = 1

if (len(sys.argv) < 0):
    print 'Error: You must specify the britefile.'
    print 'Try toposerv -h for help.'
    sys.exit()
    
# It has at least one argument
firstArg = sys.argv[1]

if firstArg == '-h' or firstArg == '--help':
    help()
    sys.exit()
elif firstArg != '-f' and firstArg != '--file':
    print 'Error: The first argument must be -h or -f'
    print 'Try toposerv -h for help.'
    sys.exit()
    
if len(sys.argv) < 3:
    print 'Error: You must specify the britefile.'
    print 'Try toposerv -h for help.'
    sys.exit()
    
fileName = sys.argv[2]

argIndex = 3
while argIndex < len(sys.argv):
    arg = sys.argv[argIndex]
    
    if arg == '-g' or arg == '--group':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            groupSize = int(sys.argv[argIndex])
            if argIndex +1 < len(sys.argv):
                nextArg = sys.argv[argIndex+1]
                if nextArg[0:1] != '-':
                    argIndex += 1
                    groupInitialSize = int(nextArg)
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
            
    elif arg == '-s' or arg == '--source':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            source = int(sys.argv[argIndex])
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
            
    elif arg == '-t' or arg == '--time':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            eventTime = int(sys.argv[argIndex])
            hasEvent = True
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
            
    elif arg == '-i' or arg == '--in':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            entryNumber = int(sys.argv[argIndex])
            entryPoisson = False
            hasEvent = True
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
            
    elif arg == '-o' or arg == '--out':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            exitNumber = int(sys.argv[argIndex])
            exitPoisson = False
            hasEvent = True
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
            
    elif arg == '-I' or arg == '--IN':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            entryNumber = int(sys.argv[argIndex])
            entryPoisson = True
            hasEvent = True
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
            
    elif arg == '-O' or arg == '--OUT':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            exitNumber = int(sys.argv[argIndex])
            exitPoisson = True
            hasEvent = True
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
            sys.exit()
    elif arg == '-d' or arg == '--delta':
        if argIndex +1 < len(sys.argv):
            argIndex += 1
            delta = int(sys.argv[argIndex])
        else:
            print 'Error: Invalid argument number.'
            print 'Try toposerv -h for help.'
        
    else:
        print 'Error: Invalid argument', arg 
        print 'Try toposerv -h for help.'
        sys.exit()
    
    argIndex += 1
    

print 'Brite File:', fileName
if groupSize != 0:
    print 'Multicast Group Size:', groupSize
else:
    print 'Multicast Group Size: Default (1/2 nodes)'
    
print 'Delta Ids:', delta
    
if groupInitialSize != 0:
    print 'Multicast Group Initial Hosts:', groupInitialSize
else:
    print 'Multicast Group Initial Hosts: Default (1/2 group size)'
    
if source != 0:
    print 'Multicast Group Initial Source:', source
else:
    print 'Multicast Group Initial Source: Random selected'
    
if hasEvent == True:
    print 'Event Interval Time (seconds):', eventTime
    if not entryPoisson:
        print 'Host\'s number for Entry Event:', entryNumber
    else:
        print 'Parameter for Poisson Distribution for Entry Event:', entryNumber
        
    if not exitPoisson:
        print 'Host\'s number for Exit Event:', exitNumber
    else:
        print 'Parameter for Poisson Distribution for Exit Event:', exitNumber      
    

topomgr = TopologyManager()
topomgr.set_event_interval(eventTime)
topomgr.set_entry_events(entryNumber, entryPoisson)
topomgr.set_exit_events(exitNumber, exitPoisson)
topomgr.importTopologyFromBrite(fileName, groupSize, groupInitialSize, source, delta)

server = TopologyServer(topomgr, hasEvent)
server.startListen()    