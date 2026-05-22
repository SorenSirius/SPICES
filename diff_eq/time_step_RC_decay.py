# cap equation C = Q/V
# V = Q/C
# dV/dt = I/C
# I' + 1/RC I = 1/R V'
# I' = 1/R V' - 1/RC * I
# dI/dt = 1/R V' - 1/RC * I

import numpy as np
import matplotlib.pyplot as plt
from math import exp
from models import Capacitor, Resistor

dt = 0.01
# Create a proper time array with integer number of points
t = np.linspace(0, 5, int(10 / dt) + 1)

w = 2 * np.pi  # 1 Hz

def source_voltage(time):

    return 1/(1+exp(-time))-1
    #return np.sin(w * time)

# initial conditions: V(0) = 0
v_prev = 0.0
i = 1.0

R = 1.0
C = 0.1
it = []
vt = []

for step in t:
    # recompute driving voltage independently
    v_step = source_voltage(step)
    vt.append(v_step)
    dv = v_step - v_prev
    dvdt = dv / dt
    v_prev = v_step

    # compute di/dt for the RC circuit
    didt = -(1 / (R * C)) * i + (1 / R) * dvdt
    i += didt * dt
    it.append(i)

#compute the voltage across the capacitor as a function of time, without knowledge of the full diff eq and instead
# just treating the cap as a current source and resistor in parallel
# Plot t on the x axis and current i(t) plus source voltage v(t) on the y axis
plt.figure(figsize=(8, 5))
plt.plot(t, it, label='i(t)')
plt.plot(t, vt, label='v(t)', linestyle='--')
plt.xlabel('Time t (s)')
plt.ylabel('Signal value')
plt.title('RC Circuit Current and Source Voltage vs Time')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()