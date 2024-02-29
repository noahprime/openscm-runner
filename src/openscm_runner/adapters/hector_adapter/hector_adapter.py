"""
Hector adapter
"""
import logging
import os.path
from subprocess import check_output  # nosec

import scmdata

from ..base import _Adapter
from .hector_wrapper import HectorWrapper

LOGGER = logging.getLogger(__name__)


def _execute_run(cfgs, output_variables, scenariodata):
    hector = HectorWrapper(scenariodata)
    try:
        out = hector.run_over_cfgs(cfgs, output_variables)
    finally:
        hector.cleanup_tempdirs()
    return out


class HECTOR(_Adapter): 
    """
    Adapter for Hector
    """

    model_name = "Hector"

    def __init__(self):
        """
        Initialise the Hector adapter
        """
        super().__init__()

    def _init_model(self): 
        pass

    def _run(self, scenarios, cfgs, output_variables, output_config=None):
        """
        Run the model.

        This method is the internal implementation of the :meth:`run` interface
        
        Parameters:
        -----------
        scenarios: ScmData
        cfgs: list
            is a list of indices to run
        output_variables: list
        output_config: list
            Should be none for Hector at least for now while not implemented
        """
        if output_config is not None:
            raise NotImplementedError("`output_config` not implemented for CICERO-SCM")

        # Create run input data (cfgs, output_variables, scenariodata) for each scenario
        runs_input = [
            {"cfgs": cfgs, "output_variables": output_variables, "scenariodata": smdf}
            for (scen, model), smdf in scenarios.timeseries().groupby(["scenario", "model"])
        ]

        # Run Hector for each scenario (inside will run for each configuration)
        runs = []
        for run_input in runs_input:
            run = _execute_run(run_input['cfgs'], run_input['output_variables'], run_input['scenariodata'])
        
        # Append resulting runs using ScmRun append method
        result = scmdata.run_append([r for r in runs if r is not None])

        # Return the results of the run
        return result

    @classmethod
    def get_version(cls):
        """
        Get the Hector version being used by this adapter

        Returns
        -------
        str
            The Hector version id
        """

        return "Hector Version"