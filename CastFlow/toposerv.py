#!/usr/bin/env python
'''
Created on Oct 20, 2011

@author: caioviel
'''

def help():
    print 'Usage: toposerv -f <FILE> [-g -s -t -i -o -I -O]'
    print'\t--file, -f <FILE>\t\tSet the brite file what will be used to generate the topology.'
    print'\t--group, -g <N> [<M>]\t\tSet the multicast group total size (<N>) and'
    print                    '\t\t\t\tand initial active hosts number (<M>).'
    print '\t--source, -s <SOURCE>\t\tSet the initial source of multicast group.'
    print '\t--time, -t <TIME>\t\tSet the time between multicast event\'s generation.'
    print '\t--in, -i <N>\t\tSet the number of hosts for entryGroup events.'
    print '\t--out, -o <N>\t\tSet the number of hosts for exitGroup events.'
    print '\t--IN, -I <N>\t\tSet the parameter for Poisson distribution for entryGroup events.'
    print '\t--OUT, -O <N>\t\tSet the parameter for Poisson distribution for exitGroup events.'

import sys
from topologyserver.TopologyServer import TopologyServer

groupSize = None
groupInitialSize = None
source = None
hasEvents = False
eventTime = None
entryPoisson = False
entryNumber = None
exitPoisson = False
exitNumber = None

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
        
    else:
        print 'Error: Invalid argument', arg 
        print 'Try toposerv -h for help.'
        sys.exit()

print 'Brite File:', fileName
if groupInitialSize != None:
    print 'Multicast Group Size:', groupInitialSize
else:
    print 'Multicast Group Size Default: (1/2) nodes'
    
groupInitialSize = None
source = None
hasEvents = False
eventTime = None
entryPoisson = False
entryNumber = None
exitPoisson = False
exitNumber = None
            
    
#server = TopologyServer(fileName)
#server.startListen()    