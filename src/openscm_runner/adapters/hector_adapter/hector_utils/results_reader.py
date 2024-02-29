"""
Class with functions for reading and formatting the results of a given Hector run
"""

import os
import pandas as pd

from scmdata import ScmRun, run_append


class HECTORREADER:  # pylint: disable=too-few-public-methods
    """
    Class to write Hector ini files
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(self, output_dir, output_fn):

        # Output directory path
        self.output_dir = output_dir 

        # Full output file / path
        self.output_file_name = os.path.join(output_dir, output_fn)
        
        ...

    def read_results(self, index, output_variables, region, scenario, model):
        """
        Read results for single run
        """

        # Read in Data
        output_data = pd.read_csv(self.output_file_name, header=1, index_col=0)
        output_data = output_data[output_data.spinup == 0]
        output_data

        # TODO: Use mapping to get from output variable to hector output variables
        # output_variables
        hector_output_variables = ['global_tas', 'CO2_concentration']

        # Pre filter down to just output filters for speed
        kept_data = output_data[output_data.variable.isin(hector_output_variables)]

        # Go through each output variable, extract the data and turn into ScmRun object
        # Append the variables together with proper metadata
        runs = []
        for variable in hector_output_variables:
            # Extract data
            variable_data = output_data[output_data.variable == variable]
            timeseries = variable_data['value'].to_numpy()
            years = variable_data.index.to_list()
            unit = variable_data['units'].iloc[0]

            # Append to runs
            runs.append(
                ScmRun(
                    pd.Series(timeseries, index=years),
                    columns={
                        "climate_model": "Hector",
                        "model": model,
                        "run_id": index,
                        "scenario": scenario,
                        "region": [region],
                        "variable": [variable],
                        "unit": [unit],
                    },
                )
            )

        # Return merged results
        return run_append(runs)
        