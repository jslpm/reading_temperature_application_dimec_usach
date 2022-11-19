import matplotlib.pyplot as plt
import nidaqmx

with nidaqmx.Task() as task:
    try:
        # Tras for reading ch0 and ch1
        task.ai_channels.add_ai_thrmcpl_chan('cDAQ1Mod1/ai0:1')
        task.timing.cfg_samp_clk_timing(10)
    except:
        raise Exception('DAQ not found!')

    while True:
        measurement = task.read()
        print(measurement)
