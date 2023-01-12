import nidaqmx

task1 = nidaqmx.Task()
task1.ai_channels.add_ai_thrmcpl_chan(
                    'cDAQ1Mod1/ai2',
                    units=nidaqmx.constants.TemperatureUnits.DEG_C,
                    thermocouple_type=nidaqmx.constants.ThermocoupleType.J
                    )

task2 = nidaqmx.Task()
task2.ai_channels.add_ai_thrmcpl_chan(
                    'cDAQ1Mod1/ai10',
                    units=nidaqmx.constants.TemperatureUnits.DEG_C,
                    thermocouple_type=nidaqmx.constants.ThermocoupleType.J
                    )

while True:
    print(f'task1: {task1.read()}')
    print(f'task2: {task2.read()}')