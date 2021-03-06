import os
import random
import sys

import snap as Snap
import swlib

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

def SelectNodes(sw):
    """
    select random nodes for distance calculations
    """

    # generate samples in the first task ...-0
    taskname = sw.GetName()
    index = taskname.split("-")
    if len(index) < 2  or  index[1] != "0":
        return

    # get all the nodes and the number of samples
    nnodes = int(sw.GetVar("nodes"))
    nsample = int(sw.GetVar("stat_tasks"))

    s = set()
    for i in range(0, nsample):
        while 1:
            n = int(random.random() * nnodes)
            if not n in s:
                break
        sw.Send(i,n,"2")
        s.add(n)

def GenGraph(sw):
    """
    generate the graph edges
    """

    # extract the stubs from the args
    # iterate through the input queue and add new items to the stub list

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    Stubs = Snap.TIntV()
    for item in msglist:

        sw.flog.write("1 got item " + item + "\n")
        sw.flog.flush()

        name = sw.GetMsgName(item)

        sw.flog.write("2 got name " + name + "\n")
        sw.flog.flush()

        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        sw.flog.write("3 got vector %d" % (Vec.Len()) + "\n")
        sw.flog.flush()

        Stubs.AddV(Vec)
        #for i in range(0,Vec.Len()):
        #    stubs.append(Vec.GetVal(i).Val)

        #sw.flog.write("4 got stubs %d" % (len(stubs)) + "\n")
        sw.flog.write("4 got stubs %d" % (Stubs.Len()) + "\n")
        sw.flog.flush()

    sw.flog.write("5 got all stubs\n")
    sw.flog.flush()

    #print taskname,stubs

    # randomize the items
    Snap.Randomize(Stubs)
    #random.shuffle(stubs)
    #print taskname + "-r",stubs

    # get the pairs
    #pairs = zip(stubs[::2], stubs[1::2])
    #print taskname,pairs

    # nodes in each task and the number of tasks
    tsize = sw.GetRange()
    ntasks = int(sw.GetVar("gen_tasks"))

    # get edges for a specific task
    Tasks = Snap.TIntIntVV(ntasks)
    Snap.AssignEdges(Stubs, Tasks, tsize)

    #print taskname,edges

    # send messages
    for i in range(0,Tasks.Len()):
        #sw.flog.write("sending task %d" % (i) + "\n")
        sw.flog.write("sending task %d, len %d" %
                            (i, Tasks.GetVal(i).Len()) + "\n")
        sw.flog.flush()
        sw.Send(i,Tasks.GetVal(i),swsnap=True)

def Worker(sw):
    #SelectNodes(sw)
    GenGraph(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"a")

    sw.SetLog(flog)
    sw.GetConfig()

    Snap.SeedRandom()
    Worker(sw)

    flog.write("finished\n")
    flog.flush()

