# read_and_plot_halvorsen.py

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import nidaqmx
import numpy as np
import time

from collections import deque

# Create task object
try:
    task = nidaqmx.Task()
    task.ai_channels.add_ai_thrmcpl_chan(
            'cDAQ1Mod1/ai0', 
            units=nidaqmx.constants.TemperatureUnits.DEG_C,
            thermocouple_type=nidaqmx.constants.ThermocoupleType.K
    )
    task.timing.cfg_samp_clk_timing(1)
    #task.start()
except:
    raise Exception("Cannot create task for accesing DAQ. Check DAQ connection.")

# Open file to save data
try:
    file = open('tempdata.txt', 'w')
    file.write('time,temp_celsius\n')
except:
    raise Exception('Cannot create file to storage data.')


# Read temperature from DAQ Device
def readDAQ(task: nidaqmx.Task):
    temp = task.read()
    return temp

# Write data function
def writeFileData(time, value):
    file.write(str(time) + ',' + str(value))
    file.write('\n')

# Initialize logging
sample_time = 1.0  # sampling time [seconds]
init_time = 0
end_time = 100
temp_min = 0
temp_max = 100
y_range = [temp_min, temp_max]
x_range = [init_time, end_time]
k = 0

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_ylim(y_range)
ax.set_xlim(x_range)

xs = np.arange(init_time, end_time + sample_time, sample_time)
ys = np.zeros_like(xs)
print(xs.shape, ys.shape)

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
def logging(it, ys, task, sample_time):
    
    value = readDAQ(task)
    current_time = it * sample_time

    writeFileData(current_time, value)
    print("time =", current_time, "[s]", "temp =", round(value, 4), "[°C]")
    
    # Add y
    ys[it] = value
    
    # Update line with new y values
    line.set_data(xs[:it + 1], ys[:it + 1])

    return line,

ani = animation.FuncAnimation(
    fig, 
    logging, 
    frames=ys.shape[0],
    fargs=(ys, task, sample_time),
    init_func=init_plot, 
    interval=1000, 
    blit=True,
    repeat=False
)

plt.show()

# Release objects
file.close()
#task.stop()
task.close()
print("Adquisition has finished!.")
