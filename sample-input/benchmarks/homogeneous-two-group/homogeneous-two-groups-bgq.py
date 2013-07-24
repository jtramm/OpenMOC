from openmoc import *
import openmoc.log as log


###############################################################################
#######################   Main Simulation Parameters   ########################
###############################################################################

num_threads = 4
track_spacing = 0.1
num_azim = 16
tolerance = 1E-3
max_iters = 1000

log.setLogLevel('NORMAL')

log.py_printf('TITLE', 'Simulating a two group homogeneous infinite medium...')
log.py_printf('HEADER', 'The reference keff = 1.72...')


###############################################################################
###########################   Creating Materials   ############################
###############################################################################

log.py_printf('NORMAL', 'Creating materials...')

infinite_medium = Material(1)
infinite_medium.setNumEnergyGroups(2)

infinite_medium.setSigmaA(0.0038, 0)
infinite_medium.setSigmaA(0.184, 1)

infinite_medium.setSigmaF(0.000625, 0)
infinite_medium.setSigmaF(0.135416667, 1)

infinite_medium.setNuSigmaF(0.0015, 0)
infinite_medium.setNuSigmaF(0.325, 1)

infinite_medium.setSigmaS(0.1, 0, 0)
infinite_medium.setSigmaS(0.117, 1, 0)
infinite_medium.setSigmaS(0.0, 0, 1)
infinite_medium.setSigmaS(1.42, 1, 1)

infinite_medium.setChi(1.0, 0)
infinite_medium.setChi(0.0, 1)

infinite_medium.setSigmaT(0.2208,0)
infinite_medium.setSigmaT(1.604, 1)


###############################################################################
###########################   Creating Surfaces   #############################
###############################################################################

log.py_printf('NORMAL', 'Creating surfaces...')

circle = Circle(x=0.0, y=0.0, radius=50.0)
left = XPlane(x=-100.0)
right = XPlane(x=100.0)
top = YPlane(y=100.0)
bottom = YPlane(y=-100.0)

left.setBoundaryType(REFLECTIVE)
right.setBoundaryType(REFLECTIVE)
top.setBoundaryType(REFLECTIVE)
bottom.setBoundaryType(REFLECTIVE)


###############################################################################
#############################   Creating Cells   ##############################
###############################################################################

log.py_printf('NORMAL', 'Creating cells...')

cells = []
cells.append(CellBasic(universe=1, material=1))
cells.append(CellBasic(universe=1, material=1))
cells.append(CellFill(universe=0, universe_fill=2))

cells[0].addSurface(halfspace=-1, surface=circle)
cells[1].addSurface(halfspace=+1, surface=circle)
cells[2].addSurface(halfspace=+1, surface=left)
cells[2].addSurface(halfspace=-1, surface=right)
cells[2].addSurface(halfspace=+1, surface=bottom)
cells[2].addSurface(halfspace=-1, surface=top)


###############################################################################
###########################   Creating Lattices   #############################
###############################################################################

log.py_printf('NORMAL', 'Creating simple pin cell lattice...')

lattice = Lattice(id=2, width_x=200.0, width_y=200.0)
lattice.setLatticeCells([[1]])


###############################################################################
##########################   Creating the Geometry   ##########################
###############################################################################

log.py_printf('NORMAL', 'Creating geometry...')

geometry = Geometry()
geometry.addMaterial(infinite_medium)
geometry.addCell(cells[0])
geometry.addCell(cells[1])
geometry.addCell(cells[2])
geometry.addLattice(lattice)
geometry.initializeFlatSourceRegions()


###############################################################################
########################   Creating the TrackGenerator   ######################
###############################################################################

log.py_printf('NORMAL', 'Initializing the track generator...')

track_generator = TrackGenerator(geometry, num_azim, track_spacing)
track_generator.generateTracks()


###############################################################################
###########################   Running a Simulation   ##########################
###############################################################################

solver = ThreadPrivateSolver(geometry, track_generator)
solver.setNumThreads(num_threads)
solver.setSourceConvergenceThreshold(tolerance)
solver.convergeSource(max_iters)
solver.printTimerReport()

log.py_printf('TITLE', 'Finished')
