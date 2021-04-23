import vtk
import sys
from pymoab import core, types


# read in expanded_tags.vtk file (CWWM file w/ scalar tags)
cwwm = sys.argv[1]
usg = vtk.vtkUnstructuredGridReader()
usg.SetFileName(cwwm)
usg.ReadAllScalarsOn()
usg.SetScalarsName('ww_n_014')
usg.Update()
data = usg.GetOutput()
#usgport = usg.GetOutputPort()

# convert USG to polydata
#pd = vtk.vtkGeometryFilter()
#pd.SetInput(data)
#pd.Update()
#pdport = pd.GetOutputPort()
#pdmap = vtk.vtkPolyDataMapper()
#pdmap.SetInputConnection(pdport)

# set values for ww_n_014
cont = vtk.vtkContourFilter()
cont.SetInputData(data)
cont.SetValue(0, 1e4)
cont.SetValue(1, 1e7)
cont.SetValue(2, 1e10)
cont.SetValue(3, 1e13)
cont.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(cont.GetOutput())
mapper.ScalarVisibilityOff()

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# create a rendering window and renderer
ren = vtk.vtkRenderer()
ren.SetBackground(0.329412, 0.34902, 0.427451)  # Paraview blue

# Assign actor to the renderer
ren.AddActor(actor)

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(750, 750)

# # convert polydata back to USG
# appendfilter = vtk.vtkAppendFilter()
# appendfilter.SetInputConnection(contport)
# appendfilter.Update()
# usg_new = vtk.vtkUnstructuredGrid()
# usg_new.ShallowCopy(appendfilter.GetOutput())
#
# # write file (USG) - needed for pymoab
# outfile = 'contour-out-usg.vtk'
# writer1 = vtk.vtkGenericDataObjectWriter()
# writer1.SetFileName(outfile)
# writer1.SetInputData(usg_new)
# writer1.Update()
# writer1.Write()
