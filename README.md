# SeaGrant Recovery Simulation

`housing_entities.py` -- Basically where the Household class is. But I called it `_entities` just in case we need to create classes for other things that don't make sense to put in `housing_resources.py`

`housing_resources.py` -- The file where resource classes are defined. Right now it organized as durables (SimPy resources) and nondurables (SimPy containers).

`housing_sim.py` -- This is where a function called simulate_housing() is defined. In the function 1) the household and resource classes get instantiated, 2) the simulation environment gets instantiated, 3) the instances get pushed into the `Household.simulate()` process, 4) the simulation run, and the household object attributes get transferred to a pandas dataframe and returned. The function is meant to be self-contained to facilitate creation of many scenario `py` and `ipynb` files that call it (e.g., rather than a single config file that gets changed or having to change the specific config file referenced within the simulation).

`test_housing_sim.py` -- This is a file that sets up household and resource input data and stuffs them into a call to `housing_sim.py` One tricky thing it does is to join inline the output dataframe from `housing_sim.py` to the original household inputs dataframe.

`test_housing_sim.ipynb` -- Similar to test_housing_sim.py but in notebook format for easier analysis.
sim_io.py -- Right now this is broken and/or deprecated. The csv/pandas stuff is no longer needed. If a csv is desired the resulting output dataframe can be easily exported. The database function that was originally in `util.py` is in this file because it makes more sense -- it is an write/output operation. But it is broken now because of the many changes made. If we continue to use it (much of the query features we get using pandas) it needs to be revised to use dataframes and reference the new variable names.

If you want to store either input or output data use corresponding directories in the repo to keep data separate from code.
