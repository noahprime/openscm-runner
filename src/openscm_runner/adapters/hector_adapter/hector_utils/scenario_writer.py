"""
Class with functions for writing Hector format emission time series files
"""

import os
import csv
import pandas as pd

# Const, file name for the default Hector emissions/constraints
DEFAULT_HECTOR_HIST_CONSTRAINTS_FN = 'default_emiss-constraints.csv'

# Const, mapping file name to convert between rcmip and Hector variables
OPENSCM_HECTOR_MAPPING_FN = 'openscm-hector-mapping.csv'


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

        # TODO: remove this line
        num = long_scenario_hector_data._get_numeric_data()
        num[num < 0] = 0

        # Read in hist emissions file primary data
        hist_emiss = pd.read_csv(os.path.join(self.input_dir, DEFAULT_HECTOR_HIST_CONSTRAINTS_FN), header=5, index_col=0)

        # Read in units from hist emiss csv file
        with open(os.path.join(self.input_dir, DEFAULT_HECTOR_HIST_CONSTRAINTS_FN)) as file:
            file_reader = csv.reader(file)
            unit_row = [row for i, row in enumerate(file_reader) if i == 4][0]

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
        Filter out data not available for use in Hector and update variable names to Hector variable names and units
        """
        # Open mapping file
        openscm_hector_mapping = pd.read_csv(os.path.join(self.input_dir, OPENSCM_HECTOR_MAPPING_FN))

        # Keep only available hector variables
        hector_scenario_data = pd.merge(long_scenario_data, openscm_hector_mapping, how='inner', left_on='variable', right_on='rcmip_variable')

        # Convert variable values by multiplying by unit conversion factor
        hector_scenario_data['value'] = hector_scenario_data['value'] * hector_scenario_data['converstion factor']

        # Update variable name and units
        hector_scenario_data['variable'] = hector_scenario_data['hector_variable']
        hector_scenario_data['unit'] = hector_scenario_data['hector_unit']

        # Keep relevant columns
        hector_scenario_data = hector_scenario_data[['model', 'region', 'scenario', 'Date', 'unit', 'variable', 'value']]

        return hector_scenario_data

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
        header += f';{self.cur_run_emis_fn}\n'
        header += f';Generated with Hector openscm adapter\n'
        units_string = ','.join(unit_row) + '\n'
        header += units_string

        return header
