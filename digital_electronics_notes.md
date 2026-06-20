## Semiconductors

### Pure Silicon
Composed of atoms in covalent bonds.

Thermal generation excites electrons out of the covalent bonds and allows them to move freely. When an electron is excited out of a bond it leaves behind a hole. We can also think of a positive current flowing when electrons are attaracted from their covalent bond into a now vacant hole. The mobility of free electrons and of holes are different, and regulated by a constant.

The amount of free electrons is equal to the amount of holes due to the neutral nature of silicon. This is a function that is strongly proportional to temperature. And follows: $n = p = n_i = B * T^{3/2}*e^{-E_g/2kT}$

From inspection of this equation we can see that the concentration of free electrons and holes is strongly dependant on temperature. It decreases as the bandgap energy increases (requiring more energy to promote electrons out of the covalent bonds.) And that it relates to several constants.

### Doped Silicon

It is possible to "dope" silicon with atoms that have a different number of protons and electrons. If you dope a silicon structure with an atom such as Phosphorus that has 5 electrons in the valence band, it will have an additional free electron. If you dope the silicon with Boron or another atom with 3 electrons in the valence band which leaves a hole that can conduct current.

We know that at thermal equilibrium that free electrons (and their complementary holes) will be generated at the same rate as they are absorbed, so the concentration of free charge will not change. 

If for the sake of argument we look at an n-type doped silicon, we know that the concentration of electrons, n, should be at least equal to the doping concentration. We can reason that it will not be below this amount because in order to make a hole to absorb a free electron, a new free electron must be created. 

We know that the rate of recombination between p and n ions is proportional to p * n. We also know that n = Nn because Nn >> ni. If we know that we must be at equilibrium then we know that the recombination rate has remained unchanged because the generation rate has remained unchanged. This means that $r*n_i^2=r*n*p$ therefore $p = {n_i^2/N_n}$

### Current flow

We can very simply define current, I, as $I = q * n * v_{drift}$ or simply, current = charge of electron * number of electrons * average velocity. Charge and density are both known quantities, so all we need to worry about is drift velocity.

#### Drift Velocity
Electrons are subject to constant acceleration from an electric field with intermitent collisions with other atoms. If we make a few basic assumptions:

$E * q = m *a$

$a = q/m *E$

$v = a/m * E * t + c$

We have our expression for velocity as a function of time for an electron subjected to an electric field in free space.

The average time between collisions can be represented as 

# TODO


## Diodes:
Macroscopic equations:

Very simplest diode analysis, if Vd >> turn on voltage, just assume a constant voltage drop accross the diode of (0.7 or whatever) and allow unlimited current to flow through it.

Forward Bias (Operating in the region when V is positive)

$I = I_s (e^{v/V_t}-1)$

Reverse Bias:

$I = -I_s$

Breakdown region:

Newton-Raphson method:
Make a guess for the value on the exponential relationship curve is then iterate.

## Mosfets

### n-mos

The n-type mosfet, or n-mos, is a semiconducting device which essentially funcitons as a voltage controlled resistor or voltage controlled current source depending on the inputs.

An n-mos transistor consists of a p-type body with 2 cut in sections of n-type silicon inlaid. Bridging the gap between the two n-type segments and laid on top of the p-mos body is an insulating material which is connected to Vg. The two n-type segments are connected to Vd and Vs respectively. Vd is where the electrons flow into and Vs is where the electrons flow from. This naturally implies that Vd is at a higher potential than Vs. 

When we apply a voltage to the gate, Vg, the insulator acts as dialectric for a parallel plate capactitor formed between Vg and the p-type body, which we connect to ground in most cases. It is useful to deal with $C_{ox}$ which is defined in terms of capacitance per unit area, $[F/{m^2}]$. We know from capacitor theory that $CV=Q$.

In the case of n-mos transistors the charge which assembles on the bottom plate of the insulator is produced by two sources. Initially the p-type body will repel its holes away from the plate, resulting in a depleted negatively charged area underneat the plate. The second source is free electorns from the abundant electrons in the n-type regions. Once the voltage difference exceeds $V_{th}$ this begins to create a conducting channel. 

In this case the free charge which has accumumlated under the plate for conduction can be modeled as $Q_s=(V_g-V_t)C_{ox}$ where $Q_s$ is the charge per unit area on the underside of the capacitor.

We know from our earlier study of current that we can define current as follows:

### Triode Region

1. $I = n * q * A * v_{drift}$

Current is equal to the number of particles per unit volume, multiplied by the velocity of the particles, multiplied by the cross sectional area of interest, times the charge per particle. $[1/m^3] * [m/s] * [m^2] * [C] = [C/s]$ Velocity is essential length per time, so if you draw a box with the velocity times time length and area width, you can multiply it by the charge density to get the total charge in that box, aka, current.

2. $I = Q_s * v_{drift}$

This equation substitutes $n * q * A$ for $Q_s$ which has units of $[C/m]$ and represents the charge per unit length along the channel. This seems like it needs further explanation for the case when the channel is not constant depth and thus has a different velocity. This will almost certainly run into issues for the case where $V_d != V_s != Gnd$ because then the charge per unit length will be different. We will have to revisit. All that really matters in measuring current is that you have some concept of how much charge is in the measured surface of interest, in this case we can simplify the calculation because we already know the charge per unit area rather than volume. 

3. $I = Q_s * E * u_n$

This equation simply swaps our drif velocity for the electric field times the electron mobility. We are only concerned with electron mobility here because only electrons carry the current in n-mos transistors. Holes will face tremendous opposition trying to get out of the n-type drain and source connections, as there are nearly 0 vacancies for holes. From unitary analysis we know [m/s] = [V/Cm] * u_n$ -> $u_n = [m^2/{Vs}]$

4. $E = V_{ds}/L$ No new field is generated within the electrically neutral p-type body and we are dealing with relatively short distances

5. $Q_s = C_{ox} * (WL) * (V_g - V_b) / L$

The charge per unit channel length can be found from the capacitor formula $C=QV$ applied to the whole gate capacitance $C_{ox} * (WL)$ and the voltage applied $V_g$ because $V_b$ is usually tied to ground.

6. $I = (C_{ox} * (W/L) * (V_g))*V_{ds}$

Combining together all the previous equations we arrive at the equation for current when the drain and source terminals are held very similar and close in potential to the body voltage.

