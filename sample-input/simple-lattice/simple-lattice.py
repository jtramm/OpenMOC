from openmoc import *
import openmoc.log as log
import openmoc.plotter as plotter
import openmoc.materialize as materialize
from openmoc.options import Options


###############################################################################
#######################   Main Simulation Parameters   ########################
###############################################################################

options = Options()

num_threads = options.getNumThreads()
track_spacing = options.getTrackSpacing()
num_azim = options.getNumAzimAngles()
tolerance = options.getTolerance()
max_iters = options.getMaxIterations()

log.set_log_level('NORMAL')


###############################################################################
###########################   Creating Materials   ############################
###############################################################################

log.py_printf('NORMAL', 'Importing materials data from HDF5...')

materials = materialize.materialize('../c5g7-materials.h5')


###############################################################################
###########################   Creating Surfaces   #############################
###############################################################################

log.py_printf('NORMAL', 'Creating surfaces...')

circles = list()
planes = list()
planes.append(XPlane(x=-2.0, name='left'))
planes.append(XPlane(x=2.0, name='right'))
planes.append(YPlane(y=-2.0, name='top'))
planes.append(YPlane(y=2.0, name='bottom'))
circles.append(Circle(x=0.0, y=0.0, radius=0.4, name='large pin'))
circles.append(Circle(x=0.0, y=0.0, radius=0.3, name='medium pin'))
circles.append(Circle(x=0.0, y=0.0, radius=0.2, name='small pin'))
for plane in planes: plane.setBoundaryType(REFLECTIVE)


###############################################################################
#############################   Creating Cells   ##############################
###############################################################################

log.py_printf('NORMAL', 'Creating cells...')

large_fuel = CellBasic(name='large pin fuel', rings=3, sectors=8)
large_fuel.setMaterial(materials['UO2'])
large_fuel.addSurface(halfspace=-1, surface=circles[0])

large_moderator = CellBasic(name='large pin moderator', sectors=8)
large_moderator.setMaterial(materials['Water'])
large_moderator.addSurface(halfspace=+1, surface=circles[0])

medium_fuel = CellBasic(name='medium pin fuel', rings=3, sectors=8)
medium_fuel.setMaterial(materials['UO2'])
medium_fuel.addSurface(halfspace=-1, surface=circles[1])

medium_moderator = CellBasic(name='medium pin moderator', sectors=8)
medium_moderator.setMaterial(materials['Water'])
medium_moderator.addSurface(halfspace=+1, surface=circles[1])

small_fuel = CellBasic(name='small pin fuel', rings=3, sectors=8)
small_fuel.setMaterial(materials['UO2'])
small_fuel.addSurface(halfspace=-1, surface=circles[2])

small_moderator = CellBasic(name='small pin moderator', sectors=8)
small_moderator.setMaterial(materials['Water'])
small_moderator.addSurface(halfspace=+1, surface=circles[2])

root_cell = CellFill(name='root cell')
root_cell.addSurface(halfspace=+1, surface=planes[0])
root_cell.addSurface(halfspace=-1, surface=planes[1])
root_cell.addSurface(halfspace=+1, surface=planes[2])
root_cell.addSurface(halfspace=-1, surface=planes[3])


###############################################################################
#                            Creating Universes
###############################################################################

log.py_printf('NORMAL', 'Creating universes...')

pin1 = Universe(name='large pin cell')
pin2 = Universe(name='medium pin cell')
pin3 = Universe(name='small pin cell')
root = Universe(name='root universe')

pin1.addCell(large_fuel)
pin1.addCell(large_moderator)
pin2.addCell(medium_fuel)
pin2.addCell(medium_moderator)
pin3.addCell(small_fuel)
pin3.addCell(small_moderator)
root.addCell(root_cell)


###############################################################################
###########################   Creating Lattices   #############################
###############################################################################

log.py_printf('NORMAL', 'Creating simple 4 x 4 lattice...')

lattice = Lattice(name='4x4 lattice')
lattice.setWidth(width_x=1.0, width_y=1.0)
lattice.setUniverses([[pin1, pin2, pin1, pin2],
                      [pin2, pin3, pin2, pin3],
                      [pin1, pin2, pin1, pin2],
                      [pin2, pin3, pin2, pin3]])
root_cell.setFill(lattice)


###############################################################################
##########################   Creating the Geometry   ##########################
###############################################################################

log.py_printf('NORMAL', 'Creating geometry...')

geometry = Geometry()
geometry.setRootUniverse(root)
geometry.initializeFlatSourceRegions()

###############################################################################
########################   Creating the TrackGenerator   ######################
###############################################################################

log.py_printf('NORMAL', 'Initializing the track generator...')

track_generator = TrackGenerator(geometry, num_azim, track_spacing)
track_generator.setNumThreads(num_threads)
track_generator.generateTracks()

###############################################################################
###########################   Running a Simulation   ##########################
###############################################################################

solver = CPUSolver(geometry, track_generator)
solver.setNumThreads(num_threads)
solver.setSourceConvergenceThreshold(tolerance)
solver.convergeSource(max_iters)
solver.printTimerReport()


###############################################################################
############################   Generating Plots   #############################
###############################################################################

log.py_printf('NORMAL', 'Plotting data...')

#plotter.plot_tracks(track_generator)
#plotter.plot_segments(track_generator)
plotter.plot_materials(geometry, gridsize=500)
plotter.plot_cells(geometry, gridsize=500)
plotter.plot_flat_source_regions(geometry, gridsize=500)
plotter.plot_fluxes(geometry, solver, energy_groups=[1,2,3,4,5,6,7])

log.py_printf('TITLE', 'Finished')
