#region imports
from ResistorNetwork import ResistorNetwork, ResistorNetwork_2

def main():
    """
    This program solves for the unknown currents in the circuit of the homework assignment.
    :return: nothing
    """
    print("Network 1:") #header network 1
    Net = ResistorNetwork()  # Instantiate a ResistorNetwork object
    Net.BuildNetworkFromFile("ResistorNetwork.txt")  # call BNFF to build the resistor network from file
    IVals = Net.AnalyzeCircuit()

    print("\nNetwork 2:") #print header network 2
    Net_2 = ResistorNetwork_2()  # Instantiate a ResistorNetwork_2 object
    Net_2.BuildNetworkFromFile("ResistorNetwork_2.txt")  #build the second resistor network from file by calling BNFF
    IVals_2 = Net_2.AnalyzeCircuit()

if __name__ == "__main__":
    main()
