# Helper functions for generating a graph to be used by the lumped circuit solver
import re
from models import Resistor, Voltage_Source, Current_Source, Capacitor, Inductor


# Graph Assembly
def parse_network(text):
    components = text.strip().splitlines()
    parsed_data = []

    for component in components:
        tokens = re.split(r'[ ,]+', component.strip())
        
        tokens = [t for t in tokens if t]
        
        parsed_data.append(tokens)
        
    return parsed_data

def assemble_network_graph(parsed_network):
    '''
    Returns a node based graph containing entries for every node with all of its connections.

    Note: Node0 is reserved for ground

    args:
    list of components
    Components should be of the form [TYPE, POSITIVE NODE, NEGATIVE NODE, params]
    '''
    graph = {}
    component_list = []
    print("Printing components from assemble graph")
    for component in parsed_network:
        # component format: type, nodes, params
        print(component)
        type = component[0]
        node1 = component[1]
        node2 = component[2]

        if(type.upper() == 'R'):
            element = Resistor(node1, node2, *component[3:])
        elif(type.upper() == 'V'):
            element = Voltage_Source(node1, node2, *component[3:])
        elif(type.upper() == 'I'):
            element = Current_Source(node1, node2, *component[3:])
        elif(type.upper() == 'C'):
            element = Capacitor(node1, node2, *component[3:])
        elif(type.upper() == 'L'):
            element = Inductor(node1, node2, *component[3:])
        
        component_list.append(element)

        if(node1 not in graph):
            graph[node1] = [element]
        else:
            graph[node1].append(element)
        
        if(node2 not in graph):
            graph[node2] = [element]
        else:
            graph[node2].append(element)

    return graph,component_list

# Graph Helper Functions

def count_voltages(component_list):
    num_voltages = 0
    for component in component_list:
        if isinstance(component, Voltage_Source):
            num_voltages += 1

    return num_voltages

def num_nodes(graph):
    return len(graph) - 1