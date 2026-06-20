from math import exp

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
"""
The diode component uses a norton equivalent and the newton-raphson method 
to converge on a solution

We take a guess at the voltage across the diode, use that to calculate
a guess current Ig from the exponential model. We use the tangent line
to the exponential model to calculate the equivalent resistance.

From here we populate the MNA matrix and then solve for the voltage across
the diode. We know that the diode also sees a "load line" from the rest
of the passive components in the circuit. The load line is decreasing
as Vd increases because the more voltage is dropped across the diode - the less voltage
is dropped across the other passive components leading to a lower voltage. If we guess too 
great a value for the current through the diode, it will lead to more voltage
being dropped across the other components of the ciruit. This will in turn
lead to less voltage being dropped across the diode. Which will show up in the difference
between our guess at the resulting voltage across the diode.
"""
class Diode(Component):
    # Reference page 1488 of microelectronic circuits
    # Vt = 25.85mV
    def __init__(self, node1, node2, I_sat, thermal_voltage, voltage, name, v_guess = 0.7):
        super().__init__(node1, node2, name, v_guess)
        self.I_sat = float(I_sat)
        self.thermal_voltage = float(thermal_voltage)
        self.voltage = float(voltage)
        self.v_guess = float(v_guess)

    def init_norton(self):
        self.g_norton = (self.v_guess*self.I_sat*exp(self.v_guess/self.thermal_v_guess))
        self.r_norton = 1/self.g_norton
        self.i_norton = self.I_sat * (exp(self.v_guess/self.thermal_v_guess)-1) - self.v_guess * self.g_norton

    def __repr__(self):
        return f"{self.node1} - {self.node2} {self.voltage}V"