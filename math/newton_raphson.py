# Example of the newton_raphson method applied to the exponential diode approximation
from math import exp, inf
from scipy import fsolve

Is = 2E-15 #saturation current
Vt = 26E-3 # thermal voltage
R = 1000 # resistor in series with diode and voltage source
Vs = 5

# diode has 1mA current at 0.7V


def I_Vd(Vd):
    return Is * (exp(Vd/Vt) - 1)

def VIR(Vd):
    return (Vs-Vd)/R

def load_line(Vd):
    return I_Vd(Vd) - VIR(Vd)

def d_load_line(Vd):
    return (Is/Vt) * exp(Vd/Vt) + 1/R

def newton(tol):
    # Guess solution (potentially using 0.7 drop method)

    # update new guess with x' = x - f(x)/f'(x) until within bounds

    Vd = 0.7
    error = load_line(Vd)
    while(abs(error) > tol):
        error = load_line(Vd)
        Vd = Vd - load_line(Vd)/d_load_line(Vd)
        
    
    return Vd, I_Vd(Vd)

print("operting voltage/current", newton(0.0001))


