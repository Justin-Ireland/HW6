#region imports
from scipy.optimize import fsolve
from Resistor import Resistor
from VoltageSource import VoltageSource
from Loop import Loop
#endregion

#region class definitions
class ResistorNetwork:
    #constructor assigned
    def __init__(self):
        """
        The resistor network consists of Loops, Resistors and Voltage Sources.
        This is the constructor for the network and it defines fields for Loops, Resistors and Voltage Sources.
        You can populate these lists manually or read them in from a file.
         """
        self.Loops = [] #initialize empty loop list in network
        self.Resistors = [] #initialize empty list of resistors
        self.VSources = [] #initialize empty list of Vsource objects in network
        #endregion
#endregion

    def BuildNetworkFromFile(self, filename):
        """
        This function reads the lines from a file and processes the file to populate the fields
        for Loops, Resistors and Voltage Sources
        :param filename: string for file to process
        :return: nothing
        """
        FileTxt = open(filename, "r").read().split('\n') # reads from file and then splits the string at the new line characters
        LineNum = 0 # a counting variable to point to the line of text to be processed from FileTxt
        #erase previous values
        self.Resistors = []
        self.VSources = []
        self.Loops = []
        FileLength = len(FileTxt)
        while LineNum < FileLength:
            lineTxt = FileTxt[LineNum].lower().strip()
            if len(lineTxt) < 1 or lineTxt[0] == '#':
                pass #skips insignificant values in text
            elif "resistor" in lineTxt:
                LineNum = self.MakeResistor(LineNum, FileTxt)
            elif "source" in lineTxt:
                LineNum = self.MakeVSource(LineNum, FileTxt)
            elif "loop" in lineTxt:
                LineNum = self.MakeLoop(LineNum, FileTxt)
            LineNum += 1 #update to linenum from zero in loop

    def MakeResistor(self, N, Txt):
        """
        Make a resistor object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        R = Resistor() #instantiate resistor object
        N += 1 #once resistor detected move to next text line
        txt = Txt[N].lower() #make txt line lower case
        while "resistor" not in txt:
            if "name" in txt:
                R.Name = txt.split('=')[1].strip()
            if "resistance" in txt:
                R.Resistance = float(txt.split('=')[1].strip())
            N += 1
            txt = Txt[N].lower() #lowercase
        self.Resistors.append(R) #append object to resistor list
        return N

    def MakeVSource(self, N, Txt):
        VS = VoltageSource()
        N += 1
        txt = Txt[N].lower()
        while "source" not in txt:
            if "name" in txt:
                VS.Name = txt.split('=')[1].strip()
            if "value" in txt:
                VS.Voltage = float(txt.split('=')[1].strip())
            if "type" in txt:
                VS.Type = txt.split('=')[1].strip()
            N += 1
            txt = Txt[N].lower()
        self.VSources.append(VS)
        return N

    def MakeLoop(self, N, Txt):
        """
        Make a resistor object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        L = Loop()
        N += 1
        txt = Txt[N].lower()
        while "loop" not in txt:
            if "name" in txt:
                L.Name = txt.split('=')[1].strip()
            if "nodes" in txt:
                txt = txt.replace(" ", "")
                L.Nodes = txt.split('=')[1].strip().split(',')
            N += 1
            txt = Txt[N].lower()
        self.Loops.append(L)
        return N

    def AnalyzeCircuit(self):
        """
        fsolve for currents in network 1
        :return:
        """
        i0 = [0, 0, 0] #initial guess defined for circuit currents
        i = fsolve(self.GetKirchoffVals, i0) #fsolve Kirchoff vals for current
        #print each value for current of network
        print("I1 = {:0.1f}".format(i[0]))
        print("I2 = {:0.1f}".format(i[1]))
        print("I3 = {:0.1f}".format(i[2]))
        return i

    def GetKirchoffVals(self, i):
        """
        This function uses Kirchoff Voltage and Current laws to analyze this specific circuit
        KVL:  The net voltage drop for a closed loop in a circuit should be zero
        KCL:  The net current flow into a node in a circuit should be zero
        :param i: a list of currents relevant to the circuit
        :return: a list of loop voltage drops and node currents
        """
        # set current in resistors in the top loop.
        self.GetResistorByName('ad').Current = i[0] #I_1 in diagram
        self.GetResistorByName('bc').Current = i[0] #I_1 in diagram
        self.GetResistorByName('cd').Current = i[2] #I_3 in diagram
        #current in resistor in bottom of loop
        self.GetResistorByName('ce').Current = i[1] #I_2 in diagram
        Node_c_Current = sum([i[0], i[1], -i[2]]) #net current node c
        KVL = self.GetLoopVoltageDrops()  #calls 2 equations
        KVL.append(Node_c_Current) #calls one equation to append to Kirchoff vals
        return KVL

    def GetElementDeltaV(self, name):
        """
        Need to retrieve either a resistor or a voltage source by name.
        :param name:
        :return:
        """
        for r in self.Resistors:
            if name == r.Name or name[::-1] == r.Name:
                return -r.DeltaV()
        for v in self.VSources:
            if name == v.Name:
                return v.Voltage
            if name[::-1] == v.Name:
                return -v.Voltage

    def GetLoopVoltageDrops(self):
        """
        This calculates the net voltage drop around a closed loop in a circuit based on the
        current flowing through resistors (cause a drop in voltage regardless of direction of traversal) or
        the value of the voltage source that have been set up as positive based on the direction of traversal.
        :return: net voltage drop for all loops in the network.
        """
        loopVoltages = []
        for L in self.Loops:
            # Traverse loops in order of nodes and add up voltage drops between nodes
            loopDeltaV = 0
            for n in range(len(L.Nodes)):
                name = L.Nodes[0] + L.Nodes[n] if n == len(L.Nodes) - 1 else L.Nodes[n] + L.Nodes[n + 1]
                loopDeltaV += self.GetElementDeltaV(name)
            loopVoltages.append(loopDeltaV)
        return loopVoltages

    def GetResistorByName(self, name):
        """
        A way to retrieve a resistor object from self.Resistors based on resistor name
        :param name:
        :return:
        """
        for r in self.Resistors:
            if r.Name == name:
                return r
    #endregion

class ResistorNetwork_2(ResistorNetwork):
    def __init__(self):
        super().__init__() #runs constructor of parent class
        #endregion
    #endregion

    def AnalyzeCircuit(self):
        """
        repeat of analyze circuit but for network 2
        as this is embedded in Network 2 class.
        fsolve for all currents in network 2
        """
        i0 = [0, 0, 0, 0]  # Additional current for the extra resistor
        i = fsolve(self.GetKirchoffVals, i0)
        print("I1 = {:0.1f}".format(i[0])) #I1 in diagram printed output
        print("I2 = {:0.1f}".format(i[1])) #I2 in diagram
        print("I3 = {:0.1f}".format(i[2])) #I3 in diagram
        print("I4 = {:0.1f}".format(i[3])) #I4 in diagram
        return i #fsolved KVL for each I

    def GetKirchoffVals(self, i):
        """
        This function uses Kirchoff Voltage and Current laws to analyze this specific circuit
        of resistor network 2
        KVL:  The net voltage drop for a closed loop in a circuit should be zero
        KCL:  The net current flow into a node in a circuit should be zero
        :param i: a list of currents relevant to the circuit
        :return: a list of loop voltage drops and node currents
        """
        self.GetResistorByName('ad').Current = i[0] #I_1 in diagram
        self.GetResistorByName('bc').Current = i[0] #I_1 in diagram
        self.GetResistorByName('cd').Current = i[2] #I_2 in diagram
        self.GetResistorByName('ce').Current = i[1] #I_3 in diagram
        self.GetResistorByName('de').Current = i[3]  #I_4 in diagram added in parallel
        Node_c_Current = sum([i[0], i[1], -i[2]]) #net current @ c
        Node_e_Current = sum([-i[3], i[2]])  #Kirchhoff equation node e
        KVL = self.GetLoopVoltageDrops() #2 equations
        KVL.append(Node_c_Current)
        KVL.append(Node_e_Current)
        return [KVL[0], KVL[1], Node_c_Current, Node_e_Current]

    #endregion
#endregion