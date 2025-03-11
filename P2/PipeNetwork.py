#region imports
from scipy.optimize import fsolve
import numpy as np
from Fluid import Fluid
from Node import Node
#endregion

class PipeNetwork():
    # region constructor
    def __init__(self, Pipes=[], Loops=[], Nodes=[], fluid=Fluid()):
        '''
        The pipe network is built from pipe, node, loop, and fluid objects.
        :param Pipes: a list of pipe objects
        :param Loops: a list of loop objects
        :param Nodes: a list of node objects
        :param fluid: a fluid object
        '''
        #region attributes
        self.loops = Loops
        self.nodes = Nodes
        self.Fluid = fluid
        self.pipes = Pipes
        #endregion
    #endregion

    # region methods
    def findFlowRates(self):
        '''
        Analyzes the pipe network and finds the flow rates in each pipe given the constraints of:
        1) No net flow into a node
        2) No net pressure drops in the loops.
        :return: a list of flow rates in the pipes
        '''
        # see how many nodes and loops there are, this is how many equation results I will return
        N = len(self.nodes) + len(self.loops)  # Number of equations
        # note that I only have 10 pipes, but need 11 variables because of the degenerate node equation at b
        Q0 = np.full(N, 10)  # Initial guess for flow rates

        def fn(q):
            '''
            Callback for fsolve. Computes mass continuity and loop equations as functions of pipe flow rates.
            :param q: an array of flow rates in pipes
            :return: an array containing flow balance at nodes and pressure losses in loops
            '''
            # Update the flow rate in each pipe object
            for i in range(len(self.pipes)):
                self.pipes[i].Q = q[i] # set volumetric flow rate from input argument q

            # Calc net flow rate at each node (should sum to zero)
            L = self.getNodeFlowRates() # call the getNodeFlowRates function of this class

            # Calc net head loss at each loop (should sum to zero)
            L += self.getLoopHeadLosses() # call the getLoopHeadLosses function of this class

            return L

        #use fsolve to find the correct flow rates
        FR = fsolve(fn, Q0)
        return FR

    def getNodeFlowRates(self):
        '''
        Retrieves net flow rates at each node.
        :return: list of net flow rates
        '''
        return [n.getNetFlowRate() for n in self.nodes]
        # each node object is responsible for calculating its own net flow rate

    def getLoopHeadLosses(self):
        '''
        Retrieves net head loss for each loop.
        :return: list of head losses
        '''
        lhl =  [l.getLoopHeadLoss() for l in self.loops]
        return lhl
        # each loop object is responsible for calculating its own net head loss

    def getPipe(self, name):
        '''
        Retrieves a pipe object by its name.
        :param name: pipe name
        :return: Pipe object by name
        '''
        for p in self.pipes:
            if name == p.Name():
                return p

    def getNodePipes(self, node):
        '''
        Returns a list of pipes connected to a given node.
        :param node: node name
        :return: list of Pipe objects
        '''
        # returns a list of pipe objects that are connected to the node object
        l = []
        for p in self.pipes:
            if p.oContainsNode(node):
                l.append(p)
        return l

    def nodeBuilt(self, node):
        '''
        Checks if a node has already been created.
        :param node: node name
        :return: True if exists, False otherwise
        '''
        for n in self.nodes:
            if n.name == node:
                return True
        return False

    def getNode(self, name):
        '''
        Retrieves a node object by name.
        :param name: node name
        :return: one of the node objects by name
        '''
        for n in self.nodes:
            if n.name == name:
                return n

    def buildNodes(self):
        '''
        Automatically creates node objects by checking the pipe endpoints.
        '''
        # automatically create the node objects by looking at the pipe ends
        for p in self.pipes:
            if self.nodeBuilt(p.startNode) == False:
                # instantiate a node object and append it to the list of nodes
                self.nodes.append(Node(p.startNode, self.getNodePipes(p.startNode)))
            if self.nodeBuilt(p.endNode) == False:
                # instantiate a node object and append it to the list of nodes
                self.nodes.append(Node(p.endNode, self.getNodePipes(p.endNode)))
    #this region prints outputs to user for FR, Net Flow, & hl
    def printPipeFlowRates(self):
        '''
        Prints the flow rate for each pipe.
        '''
        for p in self.pipes:
            p.printPipeFlowRate()

    def printNetNodeFlows(self):
        '''
        Prints net flow into each node.
        '''
        for n in self.nodes:
            print('Net flow into node {} is {:0.2f} m^3/s'.format(n.name, n.getNetFlowRate()))

    def printLoopHeadLoss(self):
        '''
        Prints head loss for each loop.
        '''
        for l in self.loops:
            print('Head loss for loop {} is {:0.2f} m'.format(l.name, l.getLoopHeadLoss()))
