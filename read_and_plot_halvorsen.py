# read_and_plot_halvorsen.py

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import nidaqmx
import numpy as np
import time

# Read from DAQ Device
def readDAQ():
    task = nidaqmx.Task()
    try:
        task.ai_channels.add_ai_thrmcpl_chan(
            'cDAQ2Mod1/ai0', 
            units=nidaqmx.constants.TemperatureUnits.DEG_C,
            thermocouple_type=nidaqmx.constants.ThermocoupleType.K
        )
    except:
        raise Exception('DAQ not found!')
    task.start()
    value = task.read()
    task.stop()
    task.close()
    return value

# Write data function
def writeFileData(t, x):
    # Open file
    file = open('tempdata.txt', 'a')

    # Write data
    time = str(t)
    value = str(round(x, 4))
    file.write(time + ',' + value)
    file.write('\n')

    # Close file
    file.close()

# Initialize logging
ts = 1  # sampling time [seconds]
init_time = 0
end_time = 100
temp_min = 0
temp_max = 30
y_range = [temp_min, temp_max]
x_range = [init_time, end_time]
k = 0

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_ylim(y_range)
ax.set_xlim(x_range)

xs = list(range(0, end_time + ts, ts))
ys = []

# Create a blank line. We will update the line in animate
line, = ax.plot([], [])

# Configure plot
plt.title('Temperature')
plt.xlabel('time [s]')
plt.ylabel('Temp [°C]')
plt.grid()

def init_plot():
    line.set_data([], [])
    return line,

# Logging temperature data from DAQ Device
def logging(i, ys, xs):
    
    value = readDAQ()
    writeFileData(xs[i], value)
    print("Temp =", round(value, 4), "°C")
    
    # Add y t list
    ys.append(value)

    # Update line with new y values
    line.set_ydata(ys)
    line.set_xdata(xs[0: i + 1])
    print(i, len(ys), len(xs[0: i + 1]))

    return line,

ani = animation.FuncAnimation(fig, logging, init_func=init_plot, fargs=(ys, xs), interval=1000, blit=True)

plt.show()
