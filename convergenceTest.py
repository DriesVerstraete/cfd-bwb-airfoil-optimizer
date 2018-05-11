__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

import os
import sys
import math
import numpy as np

from Gmsh import Gmsh
from Airfoil import Airfoil
from SU2 import SU2
from BPAirfoil import BPAirfoil
from CFDrun import CFDrun

import matplotlib.pyplot as plt


GMSH_EXE_PATH = 'gmsh/gmsh.exe'
#SU2_BIN_PATH = 'D:/prog/portable/Luftfahrt/su2-windows-latest/ExecParallel/bin/'
SU2_BIN_PATH = 'su2-windows-latest/ExecParallel/bin/'
OS_MPI_COMMAND = 'mpiexec'
SU2_USED_CORES = 4
WORKING_DIR = 'dataOut/'
INPUT_DIR = 'dataIn/'

# create working dir if necessary
if not os.path.isdir(WORKING_DIR):
    os.mkdir(WORKING_DIR)

# check if gmsh exe exists
if not os.path.isfile(GMSH_EXE_PATH):
    print('gmsh executable could not be found in: ' + GMSH_EXE_PATH)
    sys.exit(0)



##################################
### naca Test                  ###

#su2 = SU2(SU2_BIN_PATH, used_cores=SU2_USED_CORES, mpi_exec=OS_MPI_COMMAND)

def run_convergence_analysis():
    config = dict()
    config['PHYSICAL_PROBLEM'] = 'EULER'
    config['MACH_NUMBER'] = str(0.65)
    config['AOA'] = str(.0)
    config['FREESTREAM_PRESSURE'] = str(24999.8) #for altitude 10363 m
    config['FREESTREAM_TEMPERATURE'] = str(220.79) #for altitude 10363 m
    #config['GAS_CONSTANT'] = str(287.87)
    #config['REF_LENGTH'] = str(1.0)
    #config['REF_AREA'] = str(1.0)
    config['MARKER_EULER'] = '( airfoil )'
    config['MARKER_FAR'] = '( farfield )'
    config['EXT_ITER'] = str(1000)
    config['OUTPUT_FORMAT'] = 'PARAVIEW'


    innerMeshSize = np.linspace(0.001, 0.1, 21)
    outerMeshSize = np.linspace(0.1, 2., 21)
    innerMeshSize = np.flip(innerMeshSize, 0)
    outerMeshSize = np.flip(outerMeshSize, 0)

    cdList = np.zeros((len(innerMeshSize),len(outerMeshSize)))
    clList = np.zeros((len(innerMeshSize),len(outerMeshSize)))
    cmList = np.zeros((len(innerMeshSize),len(outerMeshSize)))
    eList = np.zeros((len(innerMeshSize),len(outerMeshSize)))

    ouputF = open(WORKING_DIR + '/' + 'convergenceResult.txt', 'w')

    for iI in range(0, len(innerMeshSize)):
        for iO in range(0, len(outerMeshSize)):

            projectName = 'nacaMesh_i%06d_o%06d' % (int(innerMeshSize[iI]*1000), int(outerMeshSize[iO]*1000))
            projectDir = WORKING_DIR + '/' + projectName
            #create project dir if necessary
            if not os.path.isdir(projectDir):
                os.mkdir(projectDir)

            cfd = CFDrun(projectName, used_cores=SU2_USED_CORES)
            cfd.load_airfoil_from_file(INPUT_DIR + '/naca641-212.csv')
            cfd.gmsh.innerMeshSize = innerMeshSize[iI]
            cfd.gmsh.outerMeshSize = outerMeshSize[iO]
            cfd.generate_mesh()
            cfd.su2_fix_mesh()
            cfd.su2_solve(config)
            totalCL, totalCD, totalCM, totalE = cfd.su2_parse_results()
            clList[iI][iO] = totalCL
            cdList[iI][iO] = totalCD
            cmList[iI][iO] = totalCM
            eList[iI][iO] = totalE
            ouputF.write(str(innerMeshSize[iI])+','
                         +str(outerMeshSize[iO])+','
                         +str(totalCL)+','
                         +str(totalCD)+','
                         +str(totalCM)+','
                         +str(totalE)+'\n')
            ouputF.flush()

            print('totalCL: ' + str(totalCL))
            print('totalCD: ' + str(totalCD))
            print('iI: ' + str(iI) + ' iO: ' + str(iO))


    plt.pcolor(innerMeshSize, outerMeshSize, clList)
    plt.colorbar()
    plt.show()
    print('done')

def plot_output_data():
    data = np.genfromtxt(WORKING_DIR + '/' + 'convergenceResult.txt', delimiter=',')
    x = data[:,0]
    y = data[:,1]
    cl = data[:,2]
    cd = data[:,3]
    xAx = np.unique(x)
    yAx = np.unique(y)
    clMat = np.empty((len(yAx), len(xAx)))
    clMat[:] = np.nan
    cdMat = np.empty((len(yAx), len(xAx)))
    cdMat[:] = np.nan

    for i in range(0, len(cl)):
        clMat[int(np.where(yAx == y[i])[0])][int(np.where(xAx == x[i])[0])] = cl[i]
        cdMat[int(np.where(yAx == y[i])[0])][int(np.where(xAx == x[i])[0])] = cd[i]

    plt.subplot(1, 2, 1)
    plt.pcolor(xAx, yAx, clMat)
    plt.colorbar()
    plt.subplot(1, 2, 2)
    plt.pcolor(xAx, yAx, cdMat)
    plt.colorbar()
    plt.show()


if __name__ == '__main__':
    run_convergence_analysis()
    #plot_output_data()