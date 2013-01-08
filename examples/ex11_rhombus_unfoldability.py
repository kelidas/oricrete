#-------------------------------------------------------------------------------
#
# Copyright (c) 2012, IMB, RWTH Aachen.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in simvisage/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.simvisage.com/licenses/BSD.txt
#
# Thanks for using Simvisage open source!
#
# Created on Sep 8, 2011 by: matthias

from etsproxy.traits.api import HasTraits, Range, Instance, on_trait_change, \
    Trait, Property, Constant, DelegatesTo, cached_property, Str, Delegate, \
    Button, Int, Float
from etsproxy.traits.ui.api import View, Item, Group, ButtonEditor
from etsproxy.mayavi import mlab
import numpy as np
import sympy as sm
a_, b_, c_, d_ = sm.symbols('a,b,c,d')

# own Modules
from oricrete.folding import \
    RhombusCreasePattern, CreasePattern, CreasePatternView, x_, y_

from oricrete.folding.cnstr_target_face import \
    CnstrTargetFace, r_, s_, t_

from oricrete.folding.equality_constraint import \
    Unfoldability

if __name__ == '__main__':

    L_x = 8
    L_y = 4
    cp = RhombusCreasePattern(n_steps = 1,
                              L_x = L_x,
                              L_y = L_y,
                              n_x = 1,
                              n_y = 2,
                              show_iter = False,
                              z0_ratio = 0.1,
                              MAX_ITER = 200)
    n_h = cp.n_h
    n_v = cp.n_v
    n_i = cp.n_i

    A = 0.1

    B = 0.1

    s_term = 4 * B * t_ * s_ * (1 - s_ / L_y) * r_ / L_x

    face_z_t = CnstrTargetFace(F = [r_, s_, t_ * (4 * A * r_ * (1 - r_ / L_x) - s_term)])
    n_arr = np.hstack([n_h[:, :].flatten(),
                       n_v[:, :].flatten(),
                       n_i[:, :].flatten()
                       ])
    cp.tf_lst = [(face_z_t, n_arr)]

    cp.cnstr_lhs = [[(n_h[1, 0], 0, 1.0)], # 0
                   [(n_h[0, -1], 0, 1.0)], # 1
#                    [(n_h[1, -1], 1, 1.0), (n_h[1, 0], 1, 1.0)],
                    ]

    cp.cnstr_rhs = np.zeros((len(cp.cnstr_lhs),), dtype = float)

    # @todo - renaming of methods
    # @todo - projection on the caf - to get the initial vector
    # @todo - gemetry transformator
    # @todo - derivatives of caf for the current position.
    # @todo - rthombus generator with cut-away elements
    # @todo - time step counting - save the initial step separately from the time history

    cl = cp.eqcons['cl']
    del cp.eqcons['cl']
#    del cp.eqcons['dc']

    u0 = cp.generate_X0()

    u_no_constraint = cp.solve(u0 + 1e-6)

    cp.eqcons['cl'] = cl
    u_constant_length = cp.solve(u0 + 1e-6)

    # 3 delete the constant length
    del cp.eqcons['cl']
    uf = Unfoldability(cp, connectivity = [(6, [2, 5, 3, 1, 4, 0])])
    print n_i
    print n_h
    print n_v
    #uf = Unfoldability(cp, connectivity = [(n_i[0, 0], [n_h, 5, 3, 1, 4, 0])])
    cp.eqcons['uf'] = uf
    cp.use_G_du = False
    u_unfoldable = cp.solve(u0 + 1e-6, acc = 1e-4)

    #===========================================================================
    # Unfolding
    #===========================================================================
    #
    new_nodes = cp.get_new_nodes(u_unfoldable)
    cp2 = CreasePattern(nodes = new_nodes,
                        crease_lines = cp.crease_lines,
                        facets = cp.facets,
                        n_steps = 1,
                        show_iter = True,
                        z0_ratio = 0.1,
                        MAX_ITER = 200)

    face_z_0 = CnstrTargetFace(F = [r_, s_, 0])

    cp2.tf_lst = [(face_z_0, n_arr)]

    cp2.cnstr_lhs = [[(n_h[1, 0], 0, 1.0)], # 0
#                       [(n_h[1, -1], 0, 1.0)], # 1
#                    [(n_h[1, -1], 1, 1.0), (n_h[1, 0], 1, 1.0)],
                    ]
    cp2.cnstr_rhs = np.zeros((len(cp2.cnstr_lhs),), dtype = float)

    X0 = -1e-3 * np.linalg.norm(u_unfoldable) * u_unfoldable

    u_unfolded = cp2.solve(X0, acc = 1e-5)

    #===========================================================================
    # Print results
    #===========================================================================
    u_zero = np.zeros_like(cp.nodes).flatten()
    print 'G_cl(uf_zero)', uf.get_G(u_zero, 0)
    print 'G_cl(uf_no_constraint)', uf.get_G(u_no_constraint, 0)
    print 'G_cl(uf_constant_length)', uf.get_G(u_constant_length, 0)
    print 'G_cl(uf_unfoldable)', uf.get_G(u_unfoldable, 0)
    print 'u_flattened(z)', (u_unfoldable + u_unfolded).reshape(cp2.n_n, cp2.n_d)[:, 2]


    my_model = CreasePatternView(data = cp2,
                                 ff_resolution = 30,
                                 show_cnstr = True)
    my_model.configure_traits()


