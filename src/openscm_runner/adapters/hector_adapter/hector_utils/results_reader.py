"""
Class with functions for reading and formatting the results of a given Hector run
"""

import os
import pandas as pd

from scmdata import ScmRun, run_append


# File name for Hector -> OpenSCM output variables mapping
OUTPUT_MAPPING_FN = 'openscm-hector-mapping-output-vars.csv'


class HECTORREADER:  # pylint: disable=too-few-public-methods
    """
    Class to write Hector ini files
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(self, input_dir, output_dir, output_fn):

        # Input directory path
        self.input_dir = input_dir

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

        # Widen Data
        output_wide = output_data.reset_index().pivot(index=['year', 'run_name'], columns=['variable', 'component', 'units'], values='value')

        # Get output variable mapping, and keep only chosen output_variables
        output_mapping = pd.read_csv(os.path.join(self.input_dir, OUTPUT_MAPPING_FN) )
        output_mapping = output_mapping[output_mapping['Open SCM Variable Name'].isin(output_variables)]

        # Drop chosen variables with no Hector equivalent
        output_hector_variable = output_mapping.loc[~pd.isna(output_mapping['Hector Variable Name'])]['Hector Variable Name'].to_list()

        # Map special cases
        output_hector_variable = self._special_mapping_cases(output_variables, output_wide, output_hector_variable)

        # Keep only relevant columns and finish mapping
        kept_data = self._map_trim_format(output_wide, output_hector_variable, output_mapping)

        # Go through each output variable, extract the data and turn into ScmRun object
        # Append the variables together with proper metadata
        runs = []
        for variable in output_variables:
            try:
                # Extract data
                variable_data = kept_data[kept_data.variable == variable]
                timeseries = variable_data['value'].to_numpy()
                years = variable_data['year'].to_numpy()
                unit = variable_data['units'].iloc[0]

                if len(timeseries > 0):
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
            except:
                # TODO: Log warning that requested output variable not present
                next

        # Return merged results
        return run_append(runs)

    def _special_mapping_cases(self, output_variables, output_wide, output_hector_variable):
        """
        Deals with special non-trivial mappings from Hector output variables to OpenSCM output variables
        """
        if 'Effective Radiative Forcing|Greenhouse Gases' in output_variables:
            output_wide['Effective Radiative Forcing|Greenhouse Gases', 'forcing', 'W/m2'] = output_wide['RF_tot'] - \
                (output_wide['RF_BC']+output_wide['RF_OC']+output_wide['RF_SO2']+output_wide['RF_aci']+output_wide['RF_NH3']+output_wide['RF_vol']+output_wide['RF_albedo'])
            output_hector_variable.remove('RF_tot - (RF_BC + RF_OC + RF_SO2 + RF_aci + RF_NH3 + RF_vol + RF_albedo)')
            output_hector_variable += ['Effective Radiative Forcing|Greenhouse Gases']

        if 'Effective Radiative Forcing|Aerosols' in output_variables:
            output_wide['Effective Radiative Forcing|Aerosols', 'forcing', 'W/m2'] = output_wide['RF_BC']+output_wide['RF_OC']+output_wide['RF_SO2']+output_wide['RF_aci']+output_wide['RF_NH3']
            output_hector_variable.remove('RF_BC + RF_OC + RF_SO2 + RF_aci + RF_NH3')
            output_hector_variable += ['Effective Radiative Forcing|Aerosols']

        if 'Effective Radiative Forcing|Anthropogenic' in output_variables:
            output_wide['Effective Radiative Forcing|Anthropogenic', 'forcing', 'W/m2'] = output_wide['RF_tot']-output_wide['RF_vol']
            output_hector_variable.remove('RF_tot - RF_vol')
            output_hector_variable += ['Effective Radiative Forcing|Anthropogenic']

        if 'Heat Uptake|Ocean' in output_variables:
            output_wide['Heat Uptake|Ocean', 'ocean', 'W'] = output_wide['heatflux'] * 5.100656e8 * (1-0.29)
            output_hector_variable.remove('heatflux * 5100656e8 * (1 - 0.29)')
            output_hector_variable += ['Heat Uptake|Ocean']
        
        return output_hector_variable

    def _map_trim_format(self, output_wide, output_hector_variable, output_mapping):
        """
        Maps trivial cases from Hector -> OpenSCM variables, and keeps only relevant data
        in a usable format.
        """

        # Keep only needed data columns 
        kept_output_wide = output_wide[output_hector_variable]

        # Convert back to long
        kept_output_long = kept_output_wide.melt(ignore_index=False).reset_index()

        # Map Hector variable names -> OpenSCM variable names
        kept_output_long = pd.merge(
            left = kept_output_long, 
            right = output_mapping, 
            how = 'left',
            left_on = 'variable',
            right_on = 'Hector Variable Name'
        )
        keep_vec = ~pd.isna(kept_output_long['Open SCM Variable Name'])
        kept_output_long.loc[keep_vec, 'variable'] = kept_output_long.loc[keep_vec, 'Open SCM Variable Name']

        # Again, keep relevant columns
        kept_output_long = kept_output_long[['year', 'run_name', 'units', 'variable', 'value']]

        return kept_output_long
        