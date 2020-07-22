import vtk
import sys
from pymoab import core, types


def main():
    # input file (vtk isosurface geom)
    fname = sys.argv[1]  # unstructured grid vtk file

    # read unstructured grid
    usg = vtk.vtkUnstructuredGridReader()
    usg.SetFileName(fname)
    usg.Update()
    usgport = usg.GetOutputPort()

    # convert USG to polydata
    gf = vtk.vtkGeometryFilter()
    gf.SetInputConnection(usgport)
    gf.Update()
    pdport = gf.GetOutputPort()

    # setup decimate operator
    deci = vtk.vtkDecimatePro()
    deci.SetInputConnection(pdport)

    # set decimate options
    target = 0.5
    deci.SetTargetReduction(target)  # target reduction
    deci.SetPreserveTopology(True)  # preserve topology (splitting or hole elimination not allowed)
    deci.SetSplitting(False)  # no mesh splitting allowed
    deci.SetBoundaryVertexDeletion(False)  # no boundary vertex (eddge/curve) deletion allowed
    deci.Update()
    deciport = deci.GetOutputPort()

    # convert polydata back to USG
    appendfilter = vtk.vtkAppendFilter()
    appendfilter.SetInputConnection(deciport)
    appendfilter.Update()
    usg_new = vtk.vtkUnstructuredGrid()
    usg_new.ShallowCopy(appendfilter.GetOutput())

    # write file (USG) - needed for pymoab
    outfile = './decimate-out-usg.vtk'
    writer1 = vtk.vtkGenericDataObjectWriter()
    writer1.SetFileName(outfile)
    writer1.SetInputData(usg_new)
    writer1.Update()
    writer1.Write()

    # write out polydata too
    outpoly = './decimate-out-poly.vtk'
    writer2 = vtk.vtkGenericDataObjectWriter()
    writer2.SetFileName(outpoly)
    writer2.SetInputConnection(deciport)
    writer2.Update()
    writer2.Write()

    # try reading file in w/ pymoab again
    mb = core.Core()
    mb.load_file(outfile)
    rs = mb.get_root_set()
    # get entities w/ dim=2 (should be facets)
    all_facets = mb.get_entities_by_dimension(rs, 2)
    print(all_facets)
    print(len(all_facets))
    # confirm facet type (should by tris, not polygons)
    facet_type = mb.type_from_handle(all_facets[0])
    print(facet_type)
    tris1 = mb.get_entities_by_type(rs, facet_type)
    tris2 = mb.get_entities_by_type(rs, types.MBTRI)
    polys = mb.get_entities_by_type(rs, types.MBPOLYGON)
    print(tris1, len(tris1))
    print(tris2, len(tris2))
    print(polys, len(polys))


if __name__ == "__main__":
    main()
