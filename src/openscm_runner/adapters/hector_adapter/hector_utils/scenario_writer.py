"""
Class with functions for writing Hector format emission time series files
"""

import os
import csv
import pandas as pd

# Const, file name for the default Hector emissions/constraints
DEFAULT_HECTOR_HIST_CONSTRAINTS_FN = 'default_emiss-constraints.csv'

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


def _unit_conversion():
    """
    Function from converting input scenario data into units used in Hector
    TODO: Update this once mapping file completed
    """
    ...


class SCENARIOFILEWRITER:  # pylint: disable=too-few-public-methods
    """
    Class to write Hector ini files
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(self, input_dir, run_dir, cur_run_emis_fn):

        # Set input directory path
        self.input_dir = input_dir

        # Set run directory path
        self.run_dir = run_dir

        # Set file name of output emissions timeseries file
        self.cur_run_emis_fn = cur_run_emis_fn
        
        ...

    def write_scenario_file(self, scenario_data):
        """
        Format scenario data and make emissions timeseries file for single run
        """
        
        # Convert to long format and extract just the year from time objects 
        long_scenario_data = pd.melt(scenario_data, ignore_index = False).reset_index()
        long_scenario_data['Date'] = [x.year for x in long_scenario_data.time]

        # Filter out data not available for use in Hector
        long_scenario_hector_data = self._keep_hector_variables(long_scenario_data)

        # Read in hist emissions file primary data
        hist_emiss = pd.read_csv(os.path.join(self.input_dir, DEFAULT_HECTOR_HIST_CONSTRAINTS_FN), header=5, index_col=0)

        # Read in units from hist emiss csv file
        with open(os.path.join(self.input_dir, DEFAULT_HECTOR_HIST_CONSTRAINTS_FN)) as file:
            file_reader = csv.reader(file)
            unit_row = [row for i, row in enumerate(file_reader) if i == 4][0]

        # Convert units of openscm data to Hector
        # TODO: Update once have mapping file
        long_scenario_hector_data = _unit_conversion(long_scenario_hector_data, unit_row)

        # Convert to wide format used by Hector emissions files, columns being the variables
        hector_format_data = self._long_to_hector_format(long_scenario_hector_data)

        # Combining data from default in scenario input
        scenario_data = self._combine_data(hist_emiss, hector_format_data)

        # Create header and format of csv
        header = self._create_header(unit_row, scenario_data)
        out = header + scenario_data.to_csv()

        # Save Data
        f = open(os.path.join(self.run_dir, self.cur_run_emis_fn), 'w', encoding='UTF-8')
        f.write(out)
        f.close()
        
        # Return for use in config file writing
        return(max(scenario_data.index))

    def _keep_hector_variables(self, long_scenario_data):
        """
        Filter out data not available for use in Hector and update variable names to Hector variable names
        # TODO: Update with mapping file
        """
        variables = long_scenario_data.reset_index()['variable']
        keep_vec = [True] * len(variables)
        new_variable_names = [None] * len(variables)
        for i, var in enumerate(variables):
            split_variable = var.split('|')
            if len(split_variable) == 2:
                em = split_variable[1]
                variable_type = split_variable[0].lower()
                new_variable_name = f'{em}_{variable_type}'
            else:
                new_variable_name = None
            keep_vec[i] = (new_variable_name in AVAILABLE_KEYS_MAPPING.keys())
            new_variable_names[i] = new_variable_name
        long_scenario_hector_data = long_scenario_data.copy()
        long_scenario_hector_data['variable'] = new_variable_names
        long_scenario_hector_data = long_scenario_hector_data[keep_vec]

        return long_scenario_hector_data

    def _long_to_hector_format(self, long_scenario_hector_data):
        """
        Convert to wide format used by Hector emissions files, columns being the variables
        """
        # Reshaping
        hector_format_data = long_scenario_hector_data.pivot(index=['Date'], columns=['unit', 'variable'], values='value')
        hector_format_data = hector_format_data.reset_index(col_level='variable')

        # Pull out Multicolumns into units and variable names
        colnames = hector_format_data.columns
        variables = [col[1] for col in colnames]

        # Set colnames to variable names, and the Date (year) as the index
        hector_format_data = hector_format_data.set_axis(variables, axis=1)
        hector_format_data = hector_format_data.set_index('Date')

        return(hector_format_data)

    def _combine_data(self, hist_emiss, hector_format_data):
        """
        Merge together the default hist emissions with the now converted and formatted
        scenario specific data
        """
        # Hist emissions before new input data
        old_data = hist_emiss[hist_emiss.index < min(hector_format_data.index)]

        # Replacing defult data where we have input
        new_data = hist_emiss.loc[hector_format_data.index].copy()
        new_data.loc[hector_format_data.index, hector_format_data.columns] = hector_format_data

        # Stacking data
        scenario_data = pd.concat([old_data, new_data])

        return scenario_data

    def _create_header(self, unit_row, scenario_data):
        """
        Create header and format of the emissions/constraints csv
        """
        header = ''
        header += f'{self.cur_run_emis_fn}\n'
        header += f'Generated with Hector openscm adapter\n'
        units_string = ','.join(unit_row) + '\n'
        header += units_string
        out = header + scenario_data.to_csv()

        return out
