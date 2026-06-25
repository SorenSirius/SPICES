import numpy as np
import matplotlib.pyplot as plt
import network_helper
from models import *
from print_utils import format_num, format_array
from collections import defaultdict
from math import log, exp

def populate_b_current(component, b, mna_idx):
    #KCL defined to be sum of currents entering a node
    b[mna_idx[component.node1]] += component.current
    b[mna_idx[component.node2]] -= component.current

def populate_A_conductance(component, A, mna_idx):
    #current flowing into node1 through R as a result of the voltage at node 1
    A[mna_idx[component.node1]][mna_idx[component.node1]] -= 1/component.resistance 
    #current flowing into node1 through R as a result of node2
    A[mna_idx[component.node1]][mna_idx[component.node2]] += 1/component.resistance 
    #current flowing into node2 as a result of node1
    A[mna_idx[component.node2]][mna_idx[component.node1]] += 1/component.resistance 
    #current flowing into node2 through R as a result of node2
    A[mna_idx[component.node2]][mna_idx[component.node2]] -= 1/component.resistance 

def populate_A_voltage(component, A, mna_idx):

            A[mna_idx[component.node1]][mna_idx[component.name]] += 1
            A[mna_idx[component.node2]][mna_idx[component.name]] -= 1
            A[mna_idx[component.name]][mna_idx[component.node1]] -= 1
            A[mna_idx[component.name]][mna_idx[component.node2]] += 1

def populate(component_list, graph, num_nodes, num_eqs):

    A = np.zeros((num_eqs + 1,num_eqs + 1), dtype=float) #create extra dummy ground row/col to discard eqs

    b = np.zeros(num_eqs + 1)

    idx = num_nodes
    #populate resultant vector with driving voltages ie Va = Vs
    for component in component_list:
        if isinstance(component, Voltage_Source) or isinstance(component, Voltage_Function_Source):
            b[idx] = component.voltage
            idx += 1
        
    mna_idx_to_node = ['0' for x in range(num_eqs)]
    mna_idx = {}
    idx = 0
    # map nodes to indicies on the A matrix
    for node in graph:
        if node == '0':
            mna_idx[node] = num_eqs #throw away ground
        else:
            mna_idx[node] = idx
            mna_idx_to_node[idx] = node
            idx += 1

    for component in component_list:
        if isinstance(component, Voltage_Source) or isinstance(component, Voltage_Function_Source):
            mna_idx[component.name] = idx
            mna_idx_to_node[idx] = component.name
            idx += 1

    for component in component_list:
        if isinstance(component, Capacitor) or isinstance(component, Inductor):
            populate_b_current(component.i_norton,b,mna_idx)
            populate_A_conductance(component.r_norton,A,mna_idx)

        if isinstance(component, Diode):
            component.compute_norton()
            populate_b_current(component.i_norton,b,mna_idx)
            populate_A_conductance(component.r_norton,A,mna_idx)

        if isinstance(component, Current_Source):
            populate_b_current(component, b, mna_idx)

        # populate conductivity matrix
        if isinstance(component, Resistor):
            populate_A_conductance(component, A, mna_idx)

        if isinstance(component, Switch):
            populate_A_conductance(component, A, mna_idx)
            populate_A_conductance(component.switch, A, mna_idx)

        # finish KCL with currents flowing from voltage source
        elif isinstance(component, Voltage_Source) or isinstance(component, Voltage_Function_Source):
            # we have defined the current as flowing from the pos term towards negative
            #print(component.node1, component.node2, "=", format_num(component.voltage))
            populate_A_voltage(component, A, mna_idx)
    
    return (A,b,mna_idx,mna_idx_to_node)

def update_diode(mna_idx, diode, z):

    z_grounded = np.pad(z, (0, 1), mode='constant')
    diode.voltage = z_grounded[mna_idx[diode.node1]] - z_grounded[mna_idx[diode.node2]]
    error = diode.voltage-diode.v_guess
    #print(f"We calculate {format_num(diode.voltage)} volts across diode {diode.name} after pass 1. initial guess was {format_num(diode.v_guess)}. Error: {format_num(error)}")
    diode.v_guess = max(diode.v_guess - diode.v_change_max, min(diode.v_guess+diode.v_change_max, diode.voltage))
    return error

def update_switch(mna_idx, switch, z):
    z_grounded = np.pad(z, (0, 1), mode='constant')
    switch.voltage = z_grounded[mna_idx[switch.node3]]
    switch.update_state()
    #print(f"Switch Voltage {switch.voltage}, switch state: {switch.state}, switch resistor{switch.resistance}")
    return switch.voltage
"""
On the first pass, this function will compute the norton equivalent for all diodes with the given guess voltage.

Continue to loop and solve the system of linear equations with the norton approximation

The norton approximation generates a line at a tangent to the IV curve of the diode.

Solving the system of equations determines the operating point with that linear approximation.

Diodes are linear in terms of time but nonlinear in terms of voltage, so it makes sense to solve them at each point in time.
"""
def solve_non_linear(component_list, graph, num_nodes, num_eqs, tolerance):
    loops = 0
    A,b,mna_idx, mna_idx_to_node = populate(component_list, graph, num_nodes, num_eqs)
    while(True):
        error = tolerance + 1
        diode = None
        for component in component_list:

            if(isinstance(component,Diode)):
                diode = component
                if(loops > 0):
                    error = update_diode(mna_idx, component, z)
                component.compute_norton()
                populate_b_current(component.i_norton,b,mna_idx)
                populate_A_conductance(component.r_norton,A,mna_idx)
            
            elif isinstance(component, Switch):
                if(loops > 0):
                    update_switch(mna_idx, component, z)
                    populate_A_conductance(component, A, mna_idx)
                    populate_A_conductance(component.switch, A, mna_idx)

        
        A_no_ground = A[0:-1, 0:-1] 
        b_no_ground = b[0:-1]
        z = np.linalg.solve(A_no_ground,b_no_ground)

        if(error < tolerance or loops > 10):
            return A,b,mna_idx, mna_idx_to_node, z

        loops += 1

def solve(component_list, graph, num_nodes, num_eqs, tolerance = 0):
    non_linear = False
    for component in component_list:
        if(component.non_linear == True):
            non_linear = True

    if(non_linear):
        return solve_non_linear(component_list, graph, num_nodes, num_eqs, tolerance)
    
    else:
        A,b,mna_idx, mna_idx_to_node = populate(component_list, graph, num_nodes, num_eqs)
        
        A_no_ground = A[0:-1, 0:-1] 
        b_no_ground = b[0:-1]
        z = np.linalg.solve(A_no_ground,b_no_ground)

        return A,b,mna_idx, mna_idx_to_node, z


#solves for the operating point of a circuit
def MNA(graph, component_list, non_linear = False, tolerance = 0.01):
    #uses the form Ax = b where A is a matrix generated by KCL at each node combined with KVL for each voltage source

    for i, component in enumerate(component_list):
        if isinstance(component, Capacitor):
            component_list[i] = Resistor(
                component.node1,
                component.node2,
                1e300,
                component.name
            )

        elif isinstance(component, Inductor):
            component_list[i] = Resistor(
                component.node1,
                component.node2,
                1e-300,
                component.name
            )

    # create skeleton for A (size of #nodes - 1 + #voltages)
    num_nodes = network_helper.num_nodes(graph)
    num_eqs = network_helper.count_voltages(component_list)
    num_eqs += num_nodes


    populate_args = (component_list, graph, num_nodes, num_eqs)

    A,b,mna_idx, mna_idx_to_node, z = solve(*populate_args, tolerance)

    EPS = 1e-12

    for i in range(num_nodes):
        print("Voltage at node:", mna_idx_to_node[i], f"= {format_num(z[i])}")

    for i in range(num_nodes, num_eqs):
        print("Current through Voltage Source:", mna_idx_to_node[i], f"= {format_num(z[i])}")

#Extending MNA to time varying circuits?
def MNA_time(graph, component_list, dt = 0.01, end_time = 1, plot_voltage = True, tolerance = 0):
    #uses the form Ax = b where A is a matrix generated by KCL at each node combined with KVL for each voltage source

    # initialize capacitors/inductors for simulation
    for component in component_list:
        if isinstance(component, Capacitor) or isinstance(component, Inductor):
            component.init_norton(dt)

    # create skeleton for A (size of #nodes - 1 + #voltages)
    num_nodes = network_helper.num_nodes(graph)
    num_eqs = network_helper.count_voltages(component_list)
    num_eqs += num_nodes

    #create a node translation table between the user given names and the idx of the matrix
    mna_idx_to_node = ['0' for x in range(num_eqs)]
    mna_idx = {}
    idx = 0

    # map nodes to indicies on the A matrix
    for node in graph:
        if node == '0':
            mna_idx[node] = num_eqs
        else:
            mna_idx[node] = idx
            mna_idx_to_node[idx] = node
            idx += 1
 
    time = 0
    voltage_history = defaultdict(list)
    while(time < end_time):

        populate_args = (component_list, graph, num_nodes, num_eqs)
        # We will be using KCL and always assuming that all currents are flowing into each node st their sum is 0
        A,b,mna_idx, mna_idx_to_node, z = solve(*populate_args, tolerance)

        node_to_voltage = {}
        node_to_voltage['0'] = 0

        #Find voltage at all nodes
        for i in range(num_nodes):
            node = mna_idx_to_node[i]
            voltage = z[i]
            node_to_voltage[node] = voltage
            voltage_history[node].append(voltage)

        #simple euler method
        for component in component_list:
            if(isinstance(component, Voltage_Function_Source)):
                component.update(dt)

            elif(isinstance(component, Capacitor)):
                Vc = node_to_voltage[component.node1] - node_to_voltage[component.node2]
                component.i_norton.current = -Vc * component.capacitance/dt

            elif(isinstance(component, Inductor)):
                Vl = (node_to_voltage[component.node1] - node_to_voltage[component.node2])
                component.i_norton.current =  Vl * dt / component.inductance + component.i_norton.current 
        
        time += dt

    # Plot every node voltage over time before returning
    if voltage_history and plot_voltage:
        num_steps = len(next(iter(voltage_history.values())))
        time_axis = np.arange(num_steps) * dt

        plt.figure(figsize=(10, 6))
        for node, history in voltage_history.items():
            plt.plot(time_axis, history, label=node, linewidth=2)

        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (V)')
        plt.title('Node Voltages Over Time')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return voltage_history
