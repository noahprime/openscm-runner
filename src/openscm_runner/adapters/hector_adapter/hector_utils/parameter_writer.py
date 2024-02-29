"""
Class with functions for writing Hector ini files for the given scenario and configuration
"""

import os
from configparser import ConfigParser

# TODO: This will be replaced by a mapping file
AVAILABLE_KEYS_MAPPING = {
    'ffi_emissions': ['simpleNbox'],
    'luc_emissions': ['simpleNbox'],
    'daccs_uptake': ['simpleNbox'],
    'luc_uptake': ['simpleNbox'],
    'BC_emissions': ['bc'],
    'C2F6_constrain': None,
    'C2F6_emissions': ['C2F6_halocarbon'],
    'CCl4_constrain': None,
    'CCl4_emissions': ['CCl4_halocarbon'],
    'CF4_constrain': None,
    'CF4_emissions': ['CF4_halocarbon'],
    'CFC113_constrain': None,
    'CFC113_emissions': ['CFC113_halocarbon'],
    'CFC114_constrain': None,
    'CFC114_emissions': ['CFC114_halocarbon'],
    'CFC115_constrain': None,
    'CFC115_emissions': ['CFC115_halocarbon'],
    'CFC11_constrain': None,
    'CFC11_emissions': ['CFC11_halocarbon'],
    'CFC12_constrain': None,
    'CFC12_emissions': ['CFC12_halocarbon'],
    'CH3Br_constrain': None,
    'CH3Br_emissions': ['CH3Br_halocarbon'],
    'CH3CCl3_emissions': ['CH3CCl3_halocarbon'],
    'CH3Cl_constrain': None,
    'CH3Cl_emissions': ['CH3Cl_halocarbon'],
    'CH4_constrain': None,
    'CH4_emissions': ['CH4'],
    'CO2_constrain': None,
    'CO_emissions': ['OH', 'ozone'],
    'HCFC141b_constrain': None,
    'HCFC141b_emissions': ['HCFC141b_halocarbon'],
    'HCFC142b_constrain': None,
    'HCFC142b_emissions': ['HCFC142b_halocarbon'],
    'HCFC22_constrain': None,
    'HCFC22_emissions': ['HCFC22_halocarbon'],
    'HFC125_constrain': None,
    'HFC125_emissions': ['HFC125_halocarbon'],
    'HFC134a_constrain': None,
    'HFC134a_emissions': ['HFC134a_halocarbon'],
    'HFC143a_constrain': None,
    'HFC143a_emissions': ['HFC143a_halocarbon'],
    'HFC227ea_constrain': None,
    'HFC227ea_emissions': ['HFC227ea_halocarbon'],
    'HFC23_constrain': None,
    'HFC23_emissions': ['HFC23_halocarbon'],
    'HFC245_constrain': None,
    'HFC245fa_emissions': ['HFC245fa_halocarbon'],
    'HFC32_constrain': None,
    'HFC32_emissions': ['HFC23_halocarbon'],
    'HFC365_constrain': None,
    'HFC365_emissions': None,
    'HFC4310_constrain': None,
    'HFC4310_emissions': ['HFC4310_halocarbon'],
    'N2O_constrain': None,
    'N2O_emissions': ['N2O'],
    'NH3_emissions': ['nh3'],
    'NMVOC_emissions': ['OH', 'ozone'],
    'NOX_emissions': ['OH', 'ozone'],
    'OC_emissions': ['oc'],
    'RF_albedo': ['simpleNbox'],
    'SF6_constrain': None,
    'SF6_emissions': ['SF6_halocarbon'],
    'SO2_emissions': ['so2'],
    'SV': ['so2'],
    'halon1211_constrain': None,
    'halon1211_emissions': ['halon1211_halocarbon'],
    'halon1301_constrain': None,
    'halon1301_emissions': ['halon1301_halocarbon'],
    'halon2402_constrain': None,
    'halon2402_emissions': ['halon2402_halocarbon']
}


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
        new_file_data = file_data.replace('default_emiss-constraints.csv', self.cur_run_emis_fn)

        # Write out final time
        with open(os.path.join(self.run_dir, self.cur_run_ini_fn), 'w') as output_ini_file:
            output_ini_file.write(new_file_data)

        ...
