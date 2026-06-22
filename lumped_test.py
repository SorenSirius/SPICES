import network_helper
import lumped
import matplotlib.pyplot as plt
import numpy as np

#test network generation

def plot_computed_analytical(computed, analytical, dt):
    num_steps = len(computed)
    time_axis = np.arange(num_steps) * dt

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, computed, label=computed, linewidth=2)
    plt.plot(time_axis, analytical, label=analytical, linewidth=2)

    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Computed vs Analytical over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def test_network_generation_basic():
    text = """V1, 4, 1, V5
    R1, 1, 2, R1
    R3, 2, 4, R3
    R4, 2, 3, R4
    R5, 3, 4, R5
    I0, 4, 3, I5"""
    components = network_helper.parse_network(text)
    graph = network_helper.assemble_network_graph(components)

    print(graph)

def test_network_generation_MNA():
    text = """V, Vb, Va, 5, V1
    R, Va, 0, 100, R1
    R, Vb, 0, 1000, R3
    R, Vb, Vc, 500, R4
    V, Vc, 0, 10, V2"""
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA(graph, component_list)
    lumped.MNA_time(graph, component_list, 0.1, 100)


def test_current_MNA():
    text = """I, 0, Va, 1, I1
    R Va Vb 1000 R2
    R Va 0 500 R1
    R Vb 0 1500 R3
    V Va Vb 10 V1"""
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA(graph, component_list)

def test_voltage_MNA():
    text = """R Va Vb 1000 R2
    R Va 0 500 R1
    R Vb 0 1500 R3
    V Va Vb 10 V1"""
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA(graph, component_list)

def test_time_varrying_MNA():
    text = """V, Vb, Va, 5, V1
    R, Va, 0, 100, R1
    R, Vb, 0, 1000, R3
    R, Vb, Vc, 500, R4
    C, Vc, 0, 0.001, 10, C1"""
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA_time(graph, component_list)

def test_plotting():
    text = """V, Vb, Va, 5, V1
    R, Va, 0, 100, R1
    R, Vb, 0, 1000, R3
    R, Vb, Vc, 500, R4
    C, Vc, 0, 0.001, 0, C1"""
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    voltage_history = lumped.MNA_time(graph, component_list, 0.001, 5)

    # Plot voltage histories
    plt.figure(figsize=(10, 6))
    plt.plot(voltage_history['Vc'], label='Vc', linewidth=2)
    plt.plot(voltage_history['Va'], label='Va', linewidth=2)
    plt.plot(voltage_history['Vb'], label='Vb', linewidth=2)
    plt.xlabel('Time Step')
    plt.ylabel('Voltage (V)')
    plt.title('Test Circuit')
    plt.legend()
    plt.grid(True)
    plt.show()

def exp_decay_cap_test():

    text = """C, Vc, 0, 0.001, 10, C1
    R, Vc, 0, 1000, R"""

    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    voltage_history = lumped.MNA_time(graph, component_list, 0.001, 10)

    tau = 1
    time = np.arange(0,10,0.001)
    analytical_solution = 10*np.exp(time*(-tau))

    # Plot voltage histories
    plt.figure(figsize=(10, 6))
    plt.plot(voltage_history['Vc'], label='Vc(Computed)', linewidth=2)
    plt.plot(analytical_solution, label='Vc(Analytical)', linewidth=2)
    plt.xlabel('Time Step')
    plt.ylabel('Voltage (V)')
    plt.title('Exponential Decay')
    plt.legend()
    plt.grid(True)
    plt.show()

def test_LC_basic():
    text = """C, 0, Vl, 1, 1, C1
    L, Vl, 0, 1, 0, L1
    """
    #R, Vc, 0, 1000, R"""

    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    dt = 0.01
    end_time = 10
    voltage_history = lumped.MNA_time(graph, component_list, dt, end_time, plot_voltage = True)
    vl = voltage_history['Vl']
    time = np.arange(0,end_time+dt,dt)
    analytical = np.cos(time)
    #plot_computed_analytical(vl,analytical,dt)

def test_RLC_basic():
    text = """C, Vc, Vl, 1, 1, C1
    L, Vl, 0, 1, 0, L1
    R, Vc, 0, 1000, R"""

    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA_time(graph, component_list, 0.001, 100)

def test_LR_decay():

    text = """R, 0, Vl, 1, R1
    L, Vl, 0, 1, 1, L1
    """
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    dt = 0.001
    end_time = 5

    print(graph)
    print(component_list)

    lumped.MNA_time(graph, component_list, dt, end_time)

def test_lr_charging():
    text = """R, Vs, Vl, 1, R1
    L, Vl, 0, 1, 0, L1
    V, Vs, 0, 5, V1
    """
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    dt = 0.001
    end_time = 5

    print(graph)
    print(component_list)

    lumped.MNA_time(graph, component_list, dt, end_time)

def test_lr_charging_op():
    text = """R, Vs, Vl, 1, R1
    L, Vl, 0, 1, 0, L1
    V, Vs, 0, 5, V1
    """
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    dt = 0.001
    end_time = 5

    print(graph)
    print(component_list)

    lumped.MNA(graph, component_list)

def diode_test():
    text = """R, Vs, Vd, 10, R1
    D, Vd, 0, D1
    V, 0, Vs, 10, V1
    """
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA(graph, component_list, non_linear=True, tolerance=0.01)

def diode_stability_test():
    text = """D, Vd, 0, D1
    V, 0, Vd, 0.75, V1
    """
    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    lumped.MNA(graph, component_list, non_linear=True, tolerance=0.01)

def test_LCD():
    text = """C, 0, Vl, 1, 10, C1
    L, Vl, Vd, 1, 0, L1
    D, Vd, 0, D1
    """
    #R, Vc, 0, 1000, R"""

    components = network_helper.parse_network(text)
    graph, component_list = network_helper.assemble_network_graph(components)

    print(graph)
    print(component_list)

    dt = 0.01
    end_time = 10
    voltage_history = lumped.MNA_time(graph, component_list, dt, end_time, plot_voltage = True)
    vl = voltage_history['Vl']
    time = np.arange(0,end_time+dt,dt)

#test_network_generation_MNA()
#test_current_MNA()
#test_voltage_MNA()
#test_time_varrying_MNA()
#test_plotting()
#exp_decay_cap_test()
#test_RLC_basic()
#test_LR_decay()
#test_LC_basic()
#test_lr_charging_op()
#diode_test()
#diode_stability_test()
test_LCD()