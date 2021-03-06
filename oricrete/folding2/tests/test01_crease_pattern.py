'''
Created on Nov 21, 2013

@author: rch
'''

from oricrete.folding2.crease_pattern import CreasePattern
import numpy as np

def test_crease_pattern_derived_mappings():
    '''Test the mappings including neighbors and connectivity.
    '''
    cp = CreasePattern(X=[[0, 0, 0],
                          [1, 0, 0],
                          [1, 1, 0],
                          [0, 1, 0],
                          [0.5, 0.5, 0]],
                       L=[[0, 1], [1, 2], [3, 2], [0, 3], [0, 4], [1, 4], [2, 4], [3, 4]],
                       F=[[0, 1, 4], [4, 2, 1], [2, 3, 4], [3, 0, 4]])

    # tests the counter-clockwise enumeration of facets (the second faces
    # is reversed from [4,2,1] to [1,2,4]
    assert np.all(np.equal(cp.F_N[1], [1, 2, 4]))

    # test the neighbor nodes
    assert np.all(np.equal(cp.iN_neighbors[0], [0, 1, 2, 3, 0]))

    # test the association of interior node to adjacent lines
    assert np.all(np.equal(cp.iN_L[0], [4, 5, 6, 7]))

    u = np.zeros_like(cp.x_0)

    # test the crease angles within a facet (counter-clockwise enumeration)
    assert np.allclose(cp.get_F_theta(u)[0], [0.78539816, 0.78539816, 1.57079633])

    # test the face angles around a node
    assert np.allclose(cp.iN_theta[0],
                       np.array([ 1.57079633, 1.57079633, 1.57079633, 1.57079633], dtype='f'))

    # test the face angles around a node
    assert np.allclose(cp.get_F_L_vectors_du(u)[0],
                       np.array([[-1., 1., 0., 0., 0.],
                                 [ 0., -1., 0., 0. , 1.],
                                 [ 1., 0., 0., 0., -1.]], dtype='f'))

    assert np.allclose(cp.get_F_theta_du(u), np.array([[[[  1.00000000e+00, 2.22044605e-16, -0.00000000e+00],
                                                        [ -0.00000000e+00, -1.00000000e+00, -0.00000000e+00],
                                                        [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, 1.00000000e+00, -0.00000000e+00]],

                                                        [[ -0.00000000e+00, -1.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, 2.22044605e-16, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, 1.00000000e+00, -0.00000000e+00]],

                                                        [[ -1.00000000e+00, 1.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, 1.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -2.00000000e+00, -0.00000000e+00]]],


                                                       [[[ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -2.22044605e-16, 1.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, -1.00000000e+00, -0.00000000e+00]],

                                                        [[ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -2.22044605e-16, -1.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, 1.00000000e+00, -0.00000000e+00]],

                                                        [[ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, -1.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, 1.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  2.00000000e+00, -0.00000000e+00, -0.00000000e+00]]],


                                                       [[[ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, -2.22044605e-16, -0.00000000e+00],
                                                         [ -0.00000000e+00, 1.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, -1.00000000e+00, -0.00000000e+00]],

                                                        [[ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, 1.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, -2.22044605e-16, -0.00000000e+00],
                                                         [ -1.00000000e+00, -1.00000000e+00, -0.00000000e+00]],

                                                        [[ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, -1.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, -1.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, 2.00000000e+00, -0.00000000e+00]]],


                                                       [[[ -1.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  2.22044605e-16, -1.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, 1.00000000e+00, -0.00000000e+00]],

                                                        [[  2.22044605e-16, 1.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -1.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, -1.00000000e+00, -0.00000000e+00]],

                                                        [[  1.00000000e+00, -1.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [ -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
                                                         [  1.00000000e+00, 1.00000000e+00, -0.00000000e+00],
                                                         [ -2.00000000e+00, -0.00000000e+00, -0.00000000e+00]]]])
                       )

def test_crease_pattern_angle_expressions():
    '''Test expressions evaluating angles either crease angles or dihedral angles.
    '''
    cp = CreasePattern(X=[[0, 0, 0.0],
                          [1, -0.5, 0],
                          [1, 1.5, 0],
                          [2, 0, 1.0]],
                       L=[[0, 1], [1, 2], [2, 0], [1, 3], [2, 3]],
                       F=[[1, 2, 3], [0, 1, 2]])

    u = np.zeros_like(cp.x_0)

    print 'iL_within_F0'
    print cp.iL_within_F0

    print 'iL_vectors'
    print cp.get_iL_vectors(u)

    print 'iL_normed_vectors'
    print cp.get_norm_iL_vectors(u)
    assert np.allclose(cp.get_norm_iL_vectors(u), np.array([[ 0., -1., 0.]]))

    print 'iL_F'
    print cp.iL_F

    print 'F_L'
    print cp.F_L[cp.iL_F]

    print 'F_normals'
    print cp.get_F_normals(u)

    print 'iL_psi'
    print cp.get_iL_psi(u)

    print 'iL_psi2'
    print cp.get_iL_psi2(u)

    print 'F_L_bases',
    print cp.get_F_L_bases(u)
    #print cp.get_iL_psi_du(u)

if __name__ == '__main__':
    test_crease_pattern_angle_expressions()
