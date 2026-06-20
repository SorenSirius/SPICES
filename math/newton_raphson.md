# Newton Raphson

The Newton Raphson method is a method for finding the solutions of non-linear systems of equations and relies on making an initial guess and the iteratively moving towards the solution.

## Change of varibles integration:

Ex problem:
Given a semicircular sheet of material of radius a and constant density ρ, find:

(a) the centroid of the semicircular area;
(b) the moment of inertia of the sheet of material about the diameter forming the
straight side of the semicircle.

We know that sheet means 2D. We will use polar coordinates to simplify this system. We know that the mass of an area is equal to $A * \rho$

Each differential segment of area can be considered as the length, ${dr}$, times the width, $r*d\theta$

Finding the total mass is trivial, but to find the centroid we need to consider both the mass and location of each segment of the shell.

The centroid should be $\sum{m_1*p_1+. . .+m_n*p_n}/{M}$

Written in integral form we have $\int_{-\pi/2}^{\pi/2}$