from Fluid import Fluid
from Pipe import Pipe
from Loop import Loop
from PipeNetwork import PipeNetwork

def main():
    '''
    This program analyzes flows in a given pipe network based on the following principles:
    - Flow is positive from lower to higher letter nodes.
    - Pressure decreases in the direction of flow.
    - Mass is conserved at each node.
    - The pressure loss around any loop is zero.
    '''
    # Instantiate a Fluid object to define the working fluid as water
    water = Fluid()
    roughness = 0.00025  # in meters

    # Instantiate a new PipeNetwork object
    PN = PipeNetwork()

    # Add Pipe objects to the pipe network
    PN.pipes.append(Pipe('a', 'b', 250, 300, roughness, water))
    PN.pipes.append(Pipe('a', 'c', 100, 200, roughness, water))
    PN.pipes.append(Pipe('b', 'e', 100, 200, roughness, water))
    PN.pipes.append(Pipe('c', 'd', 125, 200, roughness, water))
    PN.pipes.append(Pipe('c', 'f', 100, 150, roughness, water))
    PN.pipes.append(Pipe('d', 'e', 125, 200, roughness, water))
    PN.pipes.append(Pipe('d', 'g', 100, 150, roughness, water))
    PN.pipes.append(Pipe('e', 'h', 100, 150, roughness, water))
    PN.pipes.append(Pipe('f', 'g', 125, 250, roughness, water))
    PN.pipes.append(Pipe('g', 'h', 125, 250, roughness, water))

    # Build Node objects automatically
    PN.buildNodes()

    # Update the external flow of certain nodes
    PN.getNode('a').extFlow = 60
    PN.getNode('d').extFlow = -30
    PN.getNode('f').extFlow = -15
    PN.getNode('h').extFlow = -15

    # Add Loop objects to the pipe network
    PN.loops.append(Loop('A', [PN.getPipe('a-b'), PN.getPipe('b-e'), PN.getPipe('d-e'), PN.getPipe('c-d'), PN.getPipe('a-c')]))
    PN.loops.append(Loop('B', [PN.getPipe('c-d'), PN.getPipe('d-g'), PN.getPipe('f-g'), PN.getPipe('c-f')]))
    PN.loops.append(Loop('C', [PN.getPipe('d-e'), PN.getPipe('e-h'), PN.getPipe('g-h'), PN.getPipe('d-g')]))

    # Solve for flow rates in the pipes
    PN.findFlowRates()

    # Print output
    PN.printPipeFlowRates()
    print('\nCheck node flows:')
    PN.printNetNodeFlows()
    print('\nCheck loop head loss:')
    PN.printLoopHeadLoss()

if __name__ == "__main__":
    main()
