try:
    from . import generic as g
except BaseException:
    import generic as g


class TrianglesTest(g.unittest.TestCase):

    def test_barycentric(self):
        for m in g.get_meshes(4):
            # a simple test which gets the barycentric coordinate at each of the three
            # vertices, checks to make sure the barycentric is [1,0,0] for the vertex
            # and then converts back to cartesian and makes sure the original points
            #  are the same as the conversion and back
            for method in ['cross', 'cramer']:
                for i in range(3):
                    barycentric = g.trimesh.triangles.points_to_barycentric(
                        m.triangles, m.triangles[:, i], method=method)
                    self.assertTrue(
                        (g.np.abs(barycentric - g.np.roll([1.0, 0, 0], i)) < 1e-8).all())

                    points = g.trimesh.triangles.barycentric_to_points(
                        m.triangles, barycentric)
                    self.assertTrue(
                        (g.np.abs(points - m.triangles[:, i]) < 1e-8).all())

    def test_closest(self):
        closest = g.trimesh.triangles.closest_point(
            triangles=g.data['triangles']['triangles'],
            points=g.data['triangles']['points'])

        comparison = (closest - g.data['triangles']['closest']).all()

        self.assertTrue((comparison < 1e-8).all())
        g.log.info('finished closest check on %d triangles', len(closest))

    def test_explicit_edge_case(self):
        # taken from a real scenario where I encountered the issue
        ABC = g.np.float32([[0.51729788, 0.9469626 , 0.76545976],
                            [0.28239584, 0.22104536, 0.68622209],
                            [0.1671392 , 0.39244247, 0.61805235]])
        D = g.np.float32([0.02292462, 0.75669649, 0.20354384])
        # point D projected on ABC plane is not in ABC triangle

        mesh = g.trimesh.Trimesh(ABC, [[0,1,2]])
        tm_dist = abs(mesh.nearest.signed_distance([D]))
        # closest point is on edge AC but C is returned as closest point

        norm = lambda v: g.np.sqrt(g.np.dot(v,v))
        distToLine = lambda o, v, p: norm((o-p)-g.np.dot(o-p,v)*v)

        def distPointToEdge(U, V, P): # edge [U, V], point P
            UtoV = V - U
            UtoP = P - U
            VtoP = P - V
    
            if g.np.dot(UtoV, UtoP) <= 0:       # P is 'behind' U
                return norm(UtoP)
            elif g.np.dot(-UtoV, VtoP) <= 0:    # P is 'behind' V
                return norm(VtoP)
            else:                               # P is 'between' U and V
                return distToLine(U, UtoV/norm(UtoV), P)

        gt_dist = g.np.float32([distPointToEdge(ABC[i], ABC[(i+1)%3], D) for i in range(3)]).min()
        
        assert abs(gt_dist - tm_dist) < g.tol.merge

    def test_degenerate(self):
        tri = [[[0, 0, 0],
                [1, 0, 0],
                [-.5, 0, 0]],
               [[0, 0, 0],
                [0, 0, 0],
                [10, 10, 0]],
               [[0, 0, 0],
                [0, 0, 2],
                [0, 0, 2.2]],
               [[0, 0, 0],
                [1, 0, 0],
                [0, 1, 0]]]

        tri_gt = [False,
                  False,
                  False,
                  True]

        r = g.trimesh.triangles.nondegenerate(tri)
        self.assertTrue(len(r) == len(tri))
        self.assertTrue((r == tri_gt).all())


if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
