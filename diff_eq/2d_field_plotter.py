# in the case of first order diff eq plotters we can follow these steps:

# 1. create a matrix of x,y coordinates

# 2. find the slope at each of the coordinates

# 3. plot the vector

from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

def equation(y):
    """Calculate dy/dx = sqrt(1-y^2)"""
    return sqrt(1-pow(y,2))


# Step 1: Create a matrix of x,y coordinates from [-5,5] to [-5,5]
x = np.linspace(-1, 1, 20)
y = np.linspace(-1, 1, 20)
X, Y = np.meshgrid(x, y)

# Step 2: Find the slope at each coordinate
# dy/dx = sqrt(1-y^2), so the direction vector is (1, dy/dx)
# We need to evaluate the function at each y coordinate
dY = np.zeros_like(Y)
for i in range(Y.shape[0]):
    for j in range(Y.shape[1]):
        try:
            dY[i, j] = equation(Y[i, j])
        except:
            dY[i, j] = 0  # Handle cases where equation is undefined

# The x-component of the vector field is always 1 (implicit dx)
dX = np.ones_like(X)

# Step 3: Plot the vectors
plt.figure(figsize=(10, 10))
plt.quiver(X, Y, dX, dY, alpha=0.7)
plt.xlim(-1, 1)
plt.ylim(-1, 1)
plt.xlabel('x')
plt.ylabel('y')
plt.title('Direction Field: dy/dx = sqrt(1-y²)')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)
plt.show()


