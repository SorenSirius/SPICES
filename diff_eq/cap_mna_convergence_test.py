"""
MNA requires that we first solve KCL for each node, before writing KVL for each 
independent voltage source so that we can solve for all values.

We will be treating the capacitor as a current and voltage source and seeing whether it converges
"""