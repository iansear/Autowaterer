# from autowaterer.classes.pump import Pump

# water_pump_1 = None

# WATER_PUMP_1_RUN = 'water_pump_1.run_water_pump'


# def init_pump_1():
#     global water_pump_1
#     if water_pump_1 is None:
#         water_pump_1 = Pump(12, 1.3)
#         print('Water pump 1 initialized...')
#     else:
#         print('Water pump 1 already initialized...')


# def get_job_functions():
#     """Map stored job names to live callables. Call after init_pump_1()."""
#     return {
#         WATER_PUMP_1_RUN: water_pump_1.run_water_pump,
#     }

loaded_pumps = {}