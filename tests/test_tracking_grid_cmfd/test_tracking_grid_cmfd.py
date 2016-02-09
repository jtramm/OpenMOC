#!/usr/bin/env python

import os
import sys
import math
from collections import OrderedDict
sys.path.insert(0, os.pardir)
sys.path.insert(0, os.path.join(os.pardir, 'openmoc'))
from testing_harness import TrackingTestHarness
from input_set import GridInput

import openmoc

class TrackingGridCMFDTestHarness(TrackingTestHarness):
    """Tests tracking over a grid geometry with an overlaid CMFD mesh."""

    def __init__(self):
        super(TrackingGridCMFDTestHarness, self).__init__()
        self.input_set = GridInput()

    def _setup(self):
        """Initialize the materials, geometry, and tracks"""
        super(TrackingGridCMFDTestHarness, self)._create_geometry()

        # Initialize track objects
        tracks = self.tracks
        tracks['Diagonal Track'] = openmoc.Track()
        tracks['Nudged Diagonal Track'] = openmoc.Track()
        tracks['Horizontal Track'] = openmoc.Track()
        tracks['Vertical Track'] = openmoc.Track()
        tracks['Reverse Diagonal Track'] = openmoc.Track()

        # Set track trajectories and locations
        tracks['Diagonal Track'].setValues(-3, -3, 0, 3, 3, 0, math.atan(1))
        nudge = 1e-5
        tracks['Nudged Diagonal Track'].setValues(-3+nudge, -3, 0, 3, 3-nudge,\
                                                  0, math.atan(1))
        tracks['Horizontal Track'].setValues(-3, 0, 0, 3, 0, 0, 0)
        tracks['Vertical Track'].setValues(0, -3, 0, 0, 3, 0, math.pi/2)
        tracks['Reverse Diagonal Track'].setValues(3, 3, 0, -3, -3, 0,\
                                                   math.pi + math.atan(1))

    def _run_openmoc(self):
        """Segment tracks over the geometry and save the result to a string"""

        # Segmentize over the geometry with a fine and coarse cmfd mesh
        for m in [3, 51]:

            # Overlay simple CMFD mesh
            self._result += '{0} x {0} CMFD mesh\n'.format(m)
            geometry = self.input_set.geometry
            cmfd = openmoc.Cmfd()
            cmfd.setLatticeStructure(m, m)
            geometry.setCmfd(cmfd)
            geometry.initializeCmfd()

            # Track over the composite geometry
            super(TrackingGridCMFDTestHarness, self)._run_openmoc()

if __name__ == '__main__':
    harness = TrackingGridCMFDTestHarness()
    harness.main()
