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