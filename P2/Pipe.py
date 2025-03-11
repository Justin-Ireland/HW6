import math
import numpy as np
import random as rnd
from scipy.optimize import fsolve
from Fluid import Fluid

class Pipe():
    #region constructor
    def __init__(self, Start='A', End='B', L=100, D=200, r=0.00025, fluid=Fluid()):
        '''
        Defines a generic pipe with orientation from lowest letter to highest, alphabetically.
        :param Start: the start node (string)
        :param End: the end node (string)
        :param L: the pipe length in m (float)
        :param D: the pipe diameter in mm (float)
        :param r: the pipe roughness in m  (float)
        :param fluid:  a Fluid object (typically water)
        '''
        self.startNode = min(Start, End)  #makes sure to use lowest letter for startNode
        self.endNode = max(Start, End)  #uses highest letter for endNode
        self.length = L
        self.r = r
        self.fluid = fluid  # the fluid in the pipe

        self.d = D / 1000.0  # diameter in meters
        self.relrough = self.r / self.d  # relative roughness
        self.A = math.pi / 4.0 * self.d ** 2  # pipe cross-sectional area
        self.Q = 10  # initial guess for flow rate in L/s
        self.vel = self.V()  # calculate velocity
        self.reynolds = self.Re()  # calculate Reynolds number

    #region methods
    def V(self):
        '''
        Calculate average velocity in the pipe for volumetric flow self.Q
        :return: the average velocity in m/s
        '''
        self.vel = (self.Q / 1000) / self.A  # convert L/s to m^3/s and compute velocity
        return self.vel #avg velocity (Q/A)

    def Re(self):
        '''
        Calculate the Reynolds number under current conditions.
        :return: Reynolds number
        '''
        self.reynolds = (self.fluid.rho * self.V() * self.d) / self.fluid.mu
        # Re=rho*V*d/mu, be sure to use V() so velocity is updated.
        return self.reynolds

    def FrictionFactor(self):
        '''
        Calculates the Darcy-Weisbach friction factor based on flow conditions.
        :return: the (Darcy) friction factor
        '''
        Re = self.Re() #updates re number, assigns to local Re
        rr = self.relrough #rr for turbulent flow

        def CB(): #numpy log is ln, log10 is log base 10
            cb = lambda f: 1 / (f ** 0.5) + 2.0 * np.log10(rr / 3.7 + 2.51 / (Re * f ** 0.5))
            result = fsolve(cb, (0.01)) #fsolves for
            return result[0]

        def lam(): #laminar formula
            return 64 / Re

        if Re >= 4000:
            return CB() #return true for turbulent
        if Re <= 2000:
            return lam() #conditions to return true for laminar

        CBff = CB() #ambiguous transition flow, use norm variate weighted by Re
        Lamff = lam()
        mean = Lamff + ((Re - 2000) / (4000 - 2000)) * (CBff - Lamff) #linear interpolation for mean
        sig = 0.2 * mean #standard deviation
        return rnd.normalvariate(mean, sig) #adding randomness by normvariate

    def frictionHeadLoss(self):
        '''
        Use the Darcy-Weisbach equation to find the head loss through a section of pipe.
        :return: head loss in m of fluid
        '''
        g = 9.81  # gravity in m/s^2
        ff = self.FrictionFactor() #calculate ff
        hl = ff * (self.length / self.d) * ((self.V() ** 2) / (2 * g)) #formula for head loss in m of water
        return hl

    def getFlowHeadLoss(self, s):
        '''
        Calculate the head loss for the pipe.
        :param s: the node I'm starting with in a traversal of the pipe
        :return: the signed headloss through the pipe in m of fluid
        '''
        # while traversing a loop, if s = startNode I'm traversing in same direction as positive pipe
        nTraverse = 1 if s == self.startNode else -1
        # if flow is positive sense, scalar =1 else =-1
        nFlow = 1 if self.Q >= 0 else -1
        return nTraverse * nFlow * self.frictionHeadLoss()

    def Name(self):
        '''
        Gets the pipe name.
        :return: pipe name as a string
        '''
        return self.startNode + '-' + self.endNode

    def oContainsNode(self, node):
        '''
        Checks if the pipe is connected to a given node.
        :param node: node name
        :return: True if connected, False otherwise
        '''
        return self.startNode == node or self.endNode == node

    def printPipeFlowRate(self):
        '''
        Prints the flow rate in this pipe segment.
        '''
        print('The flow in segment {} is {:0.2f} m^3/s'.format(self.Name(), self.Q/1000))

    def getFlowIntoNode(self, n):
        '''
        Determines the flow rate into node n.
        :param n: node name
        :return: flow rate into the node (+/-Q)
        '''
        return -self.Q if n == self.startNode else self.Q
#endregion