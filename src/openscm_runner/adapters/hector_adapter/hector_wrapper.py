"""
CICEROSCM_WRAPPER for parallelisation
"""
import logging
import os
import re
import shutil
import subprocess  # nosec # have to use subprocess
import tempfile
from distutils import dir_util

import numpy as np
import pandas as pd
from scmdata import ScmRun, run_append

from ...settings import config

from .hector_utils.scenario_writer import SCENARIOFILEWRITER
from .hector_utils.parameter_writer import PARAMETERFILEWRITER
from .hector_utils.results_reader import HECTORREADER

LOGGER = logging.getLogger(__name__)


class HectorWrapper:
    """
    Hector Wrapper
    """

    def __init__(self, scenario_data):
        """
        Intialise Hector wrapper
        """
        # TODO: Initialization steps for the given scenario
        
        # Set paths
        self.input_dir = os.path.join(os.path.dirname(__file__), 'input')
        self.run_dir = os.path.join(self.input_dir, 'run_dir')

        # Set scenario_data to be available by the object
        self.scenario_data = scenario_data.copy()

        # Helper objects for writing Hector input files, and reading results
        self.sfilewriter = SCENARIOFILEWRITER(self.input_dir, self.run_dir)
        self.pamfilewriter = PARAMETERFILEWRITER(self.input_dir, self.run_dir)
        self.resultsreader = HECTORREADER()

        # Optional, could use functions already made in Cicero to assert that we're working
        # with data from a unique model/scenario pair (and know what they are)
        # self.scen = _get_unique_index_values(scenariodata, "scenario")
        # self.model = _get_unique_index_values(scenariodata, "model")

        # Create the scenario file
        self.sfilewriter.write_scenario_file(scenario_data)

    def run_over_cfgs(self, cfgs, output_variables):
        """
        Run over each configuration parameter set
        write parameterfiles, run, read results
        and make an ScmRun with results
        """

        # Create empty list of runs
        runs = []

        # For each entry in cfgs
            # Potentially need to edit/create new ini file (unless can be given as command line arguments)
            # Call Hector executable with this run's ini file
                # executable = _get_executable(self.rundir)
                # call = f"{executable} {hector ini file}"

                # LOGGER.debug("Call, %s", call)
                # subprocess.check_call(
                #     call,
                #     cwd=self.rundir,
                #     shell=True,  # nosec # have to use subprocess
                # )
            # Read in output files from hector
            # Turn output Hector data into ScmRun object (see the list of output variables below, but filter to only the ones we need to return)
            # Add new ScmRun object to list of runs

        for cfg in cfgs:
            # Write the ini file
            self.pamfilewriter.write_parameterfile(cfg, self.scenario_data)

            # Get the hector executable file
            executable = self._get_executable()


        # Return list of runs using ScmRun append function
        return run_append(runs)

        def cleanup_tempdirs():
            """
            Clean up temp data from run
            """
            ...

        def _get_executable(self):
            if platform.system() == "Windows":
                executable = os.path.join(self.input_dir, "hector.exe")
            else:
                executable = os.path.join(self.input_dir, "hector")
            return executable
            ...
        

# These are all the variables we're expected to be able to output at minimum

        # "Surface Air Temperature Change",
        # "Surface Air Ocean Blended Temperature Change",
        # "Effective Radiative Forcing",
        # "Effective Radiative Forcing|Anthropogenic",
        # "Effective Radiative Forcing|Aerosols",
        # "Effective Radiative Forcing|Aerosols|Direct Effect",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|BC",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|BC|MAGICC Fossil and Industrial",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|BC|MAGICC AFOLU",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|OC",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|OC|MAGICC Fossil and Industrial",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|OC|MAGICC AFOLU",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|SOx",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|SOx|MAGICC Fossil and Industrial",
        # "Effective Radiative Forcing|Aerosols|Direct Effect|SOx|MAGICC AFOLU",
        # "Effective Radiative Forcing|Aerosols|Indirect Effect",
        # "Effective Radiative Forcing|Greenhouse Gases",
        # "Effective Radiative Forcing|CO2",
        # "Effective Radiative Forcing|CH4",
        # "Effective Radiative Forcing|N2O",
        # "Effective Radiative Forcing|F-Gases",
        # "Effective Radiative Forcing|HFC125",
        # "Effective Radiative Forcing|HFC134a",
        # "Effective Radiative Forcing|HFC143a",
        # "Effective Radiative Forcing|HFC227ea",
        # "Effective Radiative Forcing|HFC23",
        # "Effective Radiative Forcing|HFC245fa",
        # "Effective Radiative Forcing|HFC32",
        # "Effective Radiative Forcing|HFC4310mee",
        # "Effective Radiative Forcing|CF4",
        # "Effective Radiative Forcing|C6F14",
        # "Effective Radiative Forcing|C2F6",
        # "Effective Radiative Forcing|SF6",
        # "Heat Uptake",
        # "Heat Uptake|Ocean",
        # "Atmospheric Concentrations|CO2",
        # "Atmospheric Concentrations|CH4",
        # "Atmospheric Concentrations|N2O",
        # "Net Atmosphere to Land Flux|CO2",
        # "Net Atmosphere to Ocean Flux|CO2"