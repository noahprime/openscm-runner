"""
Class with functions for writing Hector ini files for the given scenario and configuration
"""

import os
from configparser import ConfigParser


class PARAMETERFILEWRITER:  # pylint: disable=too-few-public-methods
    """
    Class to write Hector ini files
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(self, input_dir, run_dir, cur_run_ini_fn, cur_run_emis_fn):

        # Input directory
        self.input_dir = input_dir

        # Run directory
        self.run_dir = run_dir

        # File name for the current run ini file
        self.cur_run_ini_fn = cur_run_ini_fn

        # File name for the current run emissions time series
        self.cur_run_emis_fn = cur_run_emis_fn

        ...

    def write_parameterfile(self, cfg, region, scenario, model, end_year):
        """
        Make parameter file for single run
        """
        # Default .ini File Name
        default_ini_fn = f'default_config.ini'

        # Read default ini file
        config_parser = ConfigParser(inline_comment_prefixes = (";",))
        config_parser.optionxform = str
        config_parser.read(os.path.join(self.input_dir, default_ini_fn))

        # If config value is provided, update value
        for key, value in cfg.items():
            if(key == 'beta'):
                config_parser.set('simpleNbox', 'beta', str(value))
            elif(key == 'S'):
                config_parser.set('temperature', 'S', str(value))
            elif(key == 'diff'):
                config_parser.set('temperature', 'diff', str(value))
            else:
                next

        # Set run name
        config_parser.set('core', 'run_name', f'{model}_{region}_{scenario}')
        
        # Set last year
        config_parser.set('core', 'endDate', str(end_year))

        # Write out with updated constants
        with open(os.path.join(self.run_dir, self.cur_run_ini_fn), 'w') as configfile:
            config_parser.write(configfile)

        # Read in again as txt file
        with open(os.path.join(self.run_dir, self.cur_run_ini_fn), 'r') as input_ini_file:
            file_data = input_ini_file.read()

        # Replace default emissions/constraints file name with new file name
        new_file_data = file_data.replace('default_emiss-constraints.csv', f'{self.cur_run_emis_fn}')

        # Write out final time
        with open(os.path.join(self.run_dir, self.cur_run_ini_fn), 'w') as output_ini_file:
            output_ini_file.write(new_file_data)

        ...
