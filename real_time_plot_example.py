import numpy as np
import matplotlib.pyplot as plt

for i in range(10):
    y = np.random.random()
    plt.scatter(i, y)
    plt.pause(0.01)

plt.show()