import matplotlib.pyplot as plt
import nidaqmx
import numpy as np

with nidaqmx.Task() as task:
    #task.ai_channels.add_ai_thrmcpl_chan('cDAQ1Mod1/ai0')
    task.ai_channels.add_ai_thrmcpl_chan('cDAQ2Mod1/ai0')
    measurements = []

    xs = list(range(0, 100))
    ys = []

    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim([10, 30])
    ax.set_xlim([0, len(xs)])
    
    # Configure plot
    plt.title('Temperature')
    plt.xlabel('time [s]')
    plt.ylabel('Temp [°C]')
    plt.grid()
    plt.show(block=False)
    
    # Create a blank line. We will update the line in animate
    line, = ax.plot([], [])

    for i in range(100):
        ys.append(task.read())
        print('temp =', ys[-1])
        
        plt.cla()
        ax.plot(xs[:i + 1], ys)
        
        plt.draw()
        plt.pause(0.0000001)
    
    


 

        

