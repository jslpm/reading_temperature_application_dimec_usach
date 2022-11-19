import matplotlib.pyplot as plt
import nidaqmx
import numpy as np

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_thrmcpl_chan('cDAQ1Mod8/ai0')

    while True:
        measurement = task.read()
        print(measurement)

