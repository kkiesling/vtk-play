import dmsh, meshio

points = [[-2, 2], [-1.5, 1], [0, -4], [1.5, 2], [2, 6], [2, -5], [-2, -5]]
geo = dmsh.Polygon(points)
x, cells = dmsh.generate(geo, 0.5)
meshio.Mesh(x, {'triangle': cells}).write('poly.vtk', binary=False)
