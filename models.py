
class Component:
    def __init__(self, node1, node2, name):
        self.node1 = node1 #Node 1 = positive terminal connection
        self.node2 = node2 #Node 2 = negative terminal connection
        self.name = name

class Resistor(Component):
    def __init__(self, node1, node2, resistance, name):
        super().__init__(node1, node2, name)
        self.resistance = float(resistance)
    def __repr__(self):
        return f"{self.node1} - {self.node2} {self.resistance}R"

class Voltage_Source(Component):
    def __init__(self, node1, node2, voltage, name):
        super().__init__(node1, node2, name)
        self.voltage = float(voltage)
    def __repr__(self):
        return f"+{self.node1} -> -{self.node2} {self.voltage}V"

class Current_Source(Component):
    #current flowing fom node1 into node2
    def __init__(self, node1, node2, current, name):
        super().__init__(node1, node2, name)
        self.current = float(current)
    def __repr__(self):
        return f"{self.node1} - {self.node2} {self.current}A"

class Capacitor(Component):
    """
    Relations:
    C=Q/V
    Q = VC
    I = dV/dt * C
    """
    def __init__(self, node1, node2, capacitance, voltage, name):
        super().__init__(node1, node2, name)
        self.capacitance = float(capacitance)
        self.voltage = float(voltage)
    def init_norton(self, dt):
        self.r_norton = Resistor(self.node1, self.node2, dt/self.capacitance, self.name+"_n_R")
        self.i_norton = Current_Source(self.node1, self.node2, self.voltage/self.r_norton.resistance, self.name + "_n_i")
    def __repr__(self):
        return f"{self.node1} - {self.node2} {self.capacitance}F"

class Inductor(Component):
    def __init__(self, node1, node2, inductance, current, name):
        super().__init__(node1, node2, name)
        self.inductance = float(inductance)
        self.current = float(current)
    def init_norton(self, dt):
        self.r_norton = Resistor(self.node1, self.node2, self.inductance/dt, self.name+"_n_R")
        self.i_norton = Current_Source(self.node1, self.node2, self.current, self.name + "_n_i")
    def __repr__(self):
        return f"{self.node1} - {self.node2} {self.inductance}L"

class Diode(Component):
    # Reference page B-4 of microelectronic circuits
    # Vt = 25.85mV
    def __init__(self, node1, node2, I_sat, thermal_voltage, voltage, name):
        super().__init__(node1, node2, name)
        self.I_sat = float(I_sat)
        self.thermal_voltage = float(thermal_voltage)
        self.voltage = float(voltage)
    def __repr__(self):
        return f"{self.node1} - {self.node2} {self.voltage}V {self.}"