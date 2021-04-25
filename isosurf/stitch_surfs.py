import vtk
import sys
import os
from pymoab import core, types
from pymoab.skinner import Skinner
import numpy as np


# extents of the geometry
xmin = ymin = zmin = -200
xmax = ymax = zmax = 200

# global moab instance info
mb = core.Core()
sk = Skinner(mb)
isosurfs = {}


def get_edges(verts):
    all_edges = mb.get_adjacencies(verts, 1, op_type=1)
    all_verts = mb.get_connectivity(all_edges)
    verts_bad = set(all_verts) - set(verts)
    if verts_bad:
        edges_bad = mb.get_adjacencies(list(verts_bad), 1, op_type=1)
        edges_good = set(all_edges) - set(edges_bad)
        return(list(edges_good))
    else:
        return list(all_edges)


def read_files():
    # read files into meshsets
    dirname = './export-trial/vols/'
    for f in os.listdir(dirname):
        i = int(f.split('.')[0])
        fname = dirname + f
        fs = mb.create_meshset()
        mb.load_file(fname, fs)
        isosurfs[i] = {}
        isosurfs[i]['fs'] = fs


def get_vert_extents(curve_verts):
    # verts that exist on the different planes
    xmin_verts = []
    xmax_verts = []
    ymin_verts = []
    ymax_verts = []
    zmin_verts = []
    zmax_verts = []
    for cv in curve_verts:
        coord = tuple(mb.get_coords(cv))
        if coord[0] == xmin:
            xmin_verts.append(cv)
        elif coord[0] == xmax:
            xmax_verts.append(cv)
        if coord[1] == ymin:
            ymin_verts.append(cv)
        elif coord[1] == ymax:
            ymax_verts.append(cv)
        if coord[2] == zmin:
            zmin_verts.append(cv)
        elif coord[2] == zmax:
            zmax_verts.append(cv)

    remaining = set(curve_verts) -\
        set(xmin_verts) - set(xmax_verts) -\
        set(ymin_verts) - set(ymax_verts) -\
        set(zmin_verts) - set(zmax_verts)
    assert(len(remaining) == 0)

    all_ext_verts = [xmin_verts,
                     ymin_verts,
                     ymax_verts,
                     zmin_verts,
                     xmax_verts,
                     zmax_verts]

    return(all_ext_verts)


def get_surf_curves():
    # get surf curves
    for i in isosurfs.keys():
        surf_curves = {}
        for surf in isosurfs[i]['surfs']:
            tris = mb.get_entities_by_dimension(surf, 2)
            curve_verts = sk.find_skin(surf, tris, True, False)
            curve_edges = sk.find_skin(surf, tris, False, False)

            surf_curves[surf] = []
            if len(curve_verts) > 0:
                # edge exists
                # get verts and edges on geometry extent
                all_ext_verts = get_vert_extents(curve_verts)
                for ext, ext_verts in enumerate(all_ext_verts):
                    if len(ext_verts) > 0:
                        cs = mb.create_meshset()
                        mb.add_entities(cs, ext_verts)
                        ext_edges = get_edges(ext_verts)
                        mb.add_entities(cs, ext_edges)
                    else:
                        cs = -1
                    surf_curves[surf].append(cs)
            else:
                # no curves on edges
                surf_curves[surf] = [-1, -1, -1, -1, -1, -1]

        isosurfs[i]['surf_curves'] = surf_curves


def separate_surfs():
    # separate disjoint surfaces
    for i in isosurfs.keys():
        fs = isosurfs[i]['fs']
        isosurfs[i]['surfs'] = []
        all_verts = mb.get_entities_by_type(fs, types.MBVERTEX)

        # create separate surfaces
        while len(all_verts) > 0:
            # get full set of connected verts starting from a seed
            verts = [all_verts[0]]
            verts_check = [all_verts[0]]
            vtmp_all = set(verts[:])

            # gather set of all vertices that are connected to the seed
            while True:
                # check adjancency and connectedness of new vertices
                vtmp = mb.get_adjacencies(mb.get_adjacencies(verts_check,
                    2, op_type=1), 0, op_type=1)

                # add newly found verts to all list
                vtmp_all.update(set(vtmp))

                # check if different from already found verts
                if len(list(vtmp_all)) == len(verts):
                    # no more vertices are connected, so full surface
                    # has been found
                    break
                else:
                    # update vertices list to check only newly found
                    # vertices
                    verts_check = vtmp_all.difference(verts)
                    verts = list(vtmp_all)

            # get the connected set of triangles that make the single
            # surface and store into a unique meshset
            tris = mb.get_adjacencies(verts, 2, op_type=1)
            surf = mb.create_meshset()
            mb.add_entities(surf, tris)
            mb.add_entities(surf, verts)

            # store surfaces in completed list
            isosurfs[i]['surfs'].append(surf)

            # remove surface from original meshset
            mb.remove_entities(fs, tris)
            mb.remove_entities(fs, verts)

            # resassign vertices that remain
            all_verts = mb.get_entities_by_type(fs, types.MBVERTEX)


def stitch_isosurfs():
    iso_ids = sorted(isosurfs.keys())
    # compare only to the next highest one (don't need to do last isosurf)
    for i in iso_ids[:-1]:
        ext_curves_1 = isosurfs[i]['surf_curves']
        ext_curves_2 = isosurfs[i + 1]['surf_curves']

        print(ext_curves_1)
        print(ext_curves_2)



if __name__ == '__main__':
    read_files()
    separate_surfs()
    get_surf_curves()
    stitch_isosurfs()
    # try to create triangles on surf extents
