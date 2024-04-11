"""
Hector Wrapper
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
import platform
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
        # Initialization steps for the given scenario
        
        # Set paths
        self.input_dir = os.path.join(os.path.dirname(__file__), 'input')
        self.run_dir = os.path.join(self.input_dir, 'run_dir')
        self.output_dir = os.path.join(self.input_dir, 'output')
        self.logs_dir = os.path.join(self.input_dir, 'logs')

        # Set scenario_data to be available by the object
        self.scenario_data = scenario_data.copy()

        # Extract the model/scenario/region combination
        self.region = scenario_data.index[0][1].replace('/', '_')
        self.scenario = scenario_data.index[0][2].replace('/', '_')
        self.model = scenario_data.index[0][0].replace('/', '_')

        # Current Run .ini File Name
        self.cur_run_ini_fn = f'{self.model}_{self.region}_{self.scenario}_cfg.ini'

        # Current Run emissions file name
        self.cur_run_emis_fn = f'{self.model}_{self.region}_{self.scenario}_emis.csv'

        # Output file name
        self.output_fn = f'outputstream_{self.model}_{self.region}_{self.scenario}.csv'

        # Helper objects for writing Hector input files, and reading results
        self.sfilewriter = SCENARIOFILEWRITER(self.input_dir, self.run_dir, self.cur_run_emis_fn)
        self.pamfilewriter = PARAMETERFILEWRITER(self.input_dir, self.run_dir, self.cur_run_ini_fn, self.cur_run_emis_fn)
        self.resultsreader = HECTORREADER(self.input_dir, self.output_dir, self.output_fn)

        # Create the scenario file, save end_year for later use
        self.end_year = self.sfilewriter.write_scenario_file(scenario_data)


    def run_over_cfgs(self, cfgs, output_variables):
        """
        Run over each configuration parameter set
        write parameterfiles, run, read results
        and make an ScmRun with results
        """

        # Create empty list of runs
        runs = []

        for i, cfg in enumerate(cfgs):
            # Write the ini file
            self.pamfilewriter.write_parameterfile(cfg, self.region, self.scenario, self.model, self.end_year)

            # Get the hector executable file
            executable = self._get_executable()

            # param file with relative path
            param_file = os.path.join(self.run_dir, self.cur_run_ini_fn)

            # Call string
            call = f'{executable} {param_file}'

            # Call executable
            subprocess.check_call(
                call,
                cwd=self.input_dir,
                shell=True
            )

            # Read Output File
            run = self.resultsreader.read_results(i, output_variables, self.region, self.scenario, self.model)

            # Append run to list of runs
            runs.append(run)


        # Return list of runs using ScmRun append function
        return run_append(runs)

    def cleanup_tempdirs(self):
        """
        Clean up temp data from run
        """
        # Clean up run directory
        self._clean_dir('run_dir')

        # Clean up output directory
        self._clean_dir('output')

        # Clean up logs directory
        self._clean_dir('logs')
        ...

    def _clean_dir(self, dir_to_clean):
        """
        Remove files in given directory in input folder
        """
        for file_name in os.listdir(os.path.join(self.input_dir, dir_to_clean)):
            if file_name != '.gitignore':
                file_path = os.path.join(self.input_dir, dir_to_clean, file_name)
                try:
                    os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_name}. Reason: {e}')
        ...

    def _get_executable(self):
        if platform.system() == "Windows":
            executable = os.path.join(self.input_dir, "hector.exe")
        else:
            executable = os.path.join(self.input_dir, "hector")
        return executable
        

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