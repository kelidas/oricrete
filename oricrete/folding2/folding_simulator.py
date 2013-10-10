#-------------------------------------------------------------------------------
#
# Copyright (c) 2009, IMB, RWTH Aachen.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in simvisage/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.simvisage.com/licenses/BSD.txt
#
# Thanks for using Simvisage open source!
#
# Created on Jan 29, 2013 by: rch

import numpy as np

from etsproxy.traits.api import HasStrictTraits, \
    Event, Property, cached_property, Str, \
    Int, Float, Array, Bool, Dict, List, \
    Constant

from etsproxy.traits.ui.api import View
from equality_constraint import \
    IEqualityConstraint

from scipy.optimize import fmin_slsqp

import platform
import time

if platform.system() == 'Linux':
    sysclock = time.time
elif platform.system() == 'Windows':
    sysclock = time.clock

class FoldingSimulator(HasStrictTraits):
    """Class implementing the simulation procedure of the folding process
    within a time range 0..1 or 0..1 for a given number of steps.
    """
    source_config_changed = Event

    followups = List()

    traits_view = View()

    tf_lst = List([])
    '''List of target faces.

    If target face is available, than use it for initialization.
    The z component of the face is multiplied with a small init_factor
    '''

    #===========================================================================
    # Geometric data
    #===========================================================================

    L = Property()
    '''Array of crease_lines defined by pairs of node numbers.
    '''
    def _get_L(self):
        return self.cp.L

    F = Property()
    '''Array of crease facets defined by list of node numbers.
    '''
    def _get_F(self):
        return self.cp.F

    n_L = Property()
    '''Number of crease lines.
    '''
    def _get_n_L(self):
        return self.cp.n_L

    n_N = Property()
    '''Number of crease nodes.
    '''
    def _get_n_N(self):
        return self.cp.n_N

    n_D = Constant(3)
    '''Number of spatial dimensions.
    '''

    n_dofs = Property()
    '''Number of degrees of freedom.
    '''
    def _get_n_dofs(self):
        return self.cp.n_dofs

    cf_lst = Property()
    '''Number of control faces.
    '''
    def _get_cf_lst(self):
        return self.cp.cf_lst

    n_c_ff = Property()
    '''Number of control faces.
    '''
    def _get_n_c_ff(self):
        return self.cp.n_c_ff

    #===========================================================================
    # Constraint data
    #===========================================================================

    GP = List([])
    ''''Points for facet grabbing [node, facet].
        First index gives the node, second the facet.
    '''
    n_GP = Property
    ''''Number of grab points.
    '''
    def _get_n_GP(self):
        '''Number of Grabpoints'''
        return len(self.GP)

    LP = List([])
    '''Nodes movable only on a crease line Array[node,linel].
       first index gives the node, second the crease line.
    '''

    n_LP = Property
    '''Number of line points.
    '''
    def _get_n_LP(self):
        return len(self.LP)

#    TS = Array()
#    '''Surfaces as ConstraintControlFace for any Surface Cnstr.
#    '''
#    def _TS_default(self):
#        return np.zeros((0,))

    CS = Array()
    '''Control Surfaces.
    '''
    def _CS_default(self):
        return np.zeros((0,))

    # constrained node indices
    # define the pairs (node, dimension) affected by the constraint
    # stored in the constrained_x array
    #
    # define the constraint in the form
    # cnstr_lhs = [ [(node_1, dir_1, coeff_1),(node_2, dir_2, coeff_2)], # first constraint
    #              [(node_i, dir_i, coeff_i)], # second constraint
    # cnstr_rhs = [ value_first, velue_second ]
    #
    # left-hand side coefficients of the constraint equations
    cnstr_lhs = List()
    # right-hand side values of the constraint equations
    cnstr_rhs = Property(depends_on='cnstr_lhs')
    @cached_property
    def _get_cnstr_rhs(self):
        return np.zeros((len(self.cnstr_lhs),), dtype='float_')

    dof_constraints = Array
    '''List of explicit constraints specified as a linear equation.
    '''

    #===========================================================================
    # Equality constraints
    #===========================================================================
    eqcons = Dict(Str, IEqualityConstraint)
    def _eqcons_default(self):
        return {}

    eqcons_lst = Property(depends_on='eqcons')
    @cached_property
    def _get_eqcons_lst(self):
        return self.eqcons.values()

    #===========================================================================
    # Solver parameters
    #===========================================================================

    n_steps = Int(1, auto_set=False, enter_set=True)
    '''Number of time steps.
    '''

    time_arr = Array(float, auto_set=False, enter_set=True)
    '''User specified time array overriding the default one.
    '''

    unfold = Bool(False)
    '''Reverse the time array. So it's possible to unfold
    a structure. If you optimize a pattern with FormFinding
    you can unfold it at least with Folding to it's flatten
    shape.
    '''

    t_arr = Property(Array(float), depends_on='unfold, n_steps, time_array')
    '''Generated time array.
    '''
    @cached_property
    def _get_t_arr(self):
        if len(self.time_arr) > 0:
            return self.time_arr
        t_arr = np.linspace(0, 1., self.n_steps + 1)
        if(self.unfold):
            # time array will be reversed if unfold is true
            t_arr = t_arr[::-1]
        return t_arr


    # show_iter saves the first 10 iterationsteps, so they'll can be
    # analized
    show_iter = Bool(False, auto_set=False, enter_set=True)

    MAX_ITER = Int(100, auto_set=False, enter_set=True)

    acc = Float(1e-4, auto_set=False, enter_set=True)

    U_t = Property(depends_on='source_config_changed, unfold')
    '''Displacement history for the current folding process.
    '''
    @cached_property
    def _get_U_t(self):
        '''Solve the problem with the appropriate solver
        '''
        time_start = sysclock()

        if(len(self.tf_lst) > 0):
            U_t = self._solve_fmin(self.U_0, self.acc)
        else:
            U_t = self._solve_nr(self.U_0, self.acc)

        time_end = sysclock()
        print '==== solved in ', time_end - time_start, '====='

        return U_t

    def _solve_nr(self, U_0, acc=1e-4):
        '''Find the solution using the Newton - Raphson procedure.
        '''
        print '==== solving with Newton-Raphson ===='

        U = np.copy(U_0)
        # Newton-Raphson iteration
        MAX_ITER = self.MAX_ITER
        U_t0 = self.U_0
        U_t = [U_t0]

        # time loop without the initial time step
        for t in self.t_arr[1:]:
            print 'step', t,

            i = 0

            while i <= MAX_ITER:
                dR = self.get_G_du(U, t)
                R = self.get_G(U, t)
                nR = np.linalg.norm(R)
                if nR < acc:
                    print '==== converged in ', i, 'iterations ===='
                    U_t.append(np.copy(U))
                    break
                try:
                    dU = np.linalg.solve(dR, -R)

                    U += dU
                    if self.show_iter:
                        U_t.append(np.copy(U))
                    i += 1
                except Exception as inst:
                    print '==== problems solving linalg in interation step %d  ====' % i
                    print '==== Exception message: ', inst
                    U_t.append(np.copy(U))
                    return U_t
            else:
                print '==== did not converge in %d interations ====' % i
                return U_t
        return np.array(U_t, dtype='f')

    use_G_du = Bool(True, auto_set=False, enter_set=True)

    t = Float(0.0, auto_set=False, enter_set=True)

    def _solve_fmin(self, U_0, acc=1e-4):
        '''Solve the problem using the
        Sequential Least Square Quadratic Programming method.
        '''
        print '==== solving with SLSQP optimization ===='
        d0 = self.get_f(U_0)
        eps = d0 * 1e-4
        U = np.copy(U_0)
        U_t0 = self.U_0
        U_t = [U_t0]
        get_G_du_t = None

        for step, time in enumerate(self.t_arr[1:]):
            print 'step', step,
            self.t = time
            if self.use_G_du:
                get_G_du_t = self.get_G_du_t

            info = fmin_slsqp(self.get_f_t, U,
                              fprime=self.get_f_du_t,
                              f_eqcons=self.get_G_t,
                              fprime_eqcons=get_G_du_t,
                              acc=acc, iter=self.MAX_ITER,
                              iprint=0,
                              full_output=True,
                              epsilon=eps)
            U, f, n_iter, imode, smode = info
            U = np.array(U, dtype='f')
            U_t.append(np.copy(U))
            if imode == 0:
                print '(time: %g, iter: %d, f: %g)' % (time, n_iter, f)
            else:
                print '(time: %g, iter: %d, f: %g, %s)' % (time, n_iter, f, smode)
                break
        return np.array(U_t, dtype='f')

    #===========================================================================
    # Goal function
    #===========================================================================
    def get_f(self, U, t=0):
        # build dist-vektor for all caf
        u = U.reshape(self.n_N, self.n_D)
        x = self.get_new_nodes(u)
        d_arr = np.array([])
        for caf, nodes in self.tf_lst:
            caf.X_arr = x[nodes]
            caf.t = t
            d_arr = np.append(d_arr, caf.d_arr)

        return np.linalg.norm(d_arr)

    def get_f_t(self, U):
        return self.get_f(U, self.t)

    #===========================================================================
    # Distance derivative with respect to change in nodal coords.
    #===========================================================================
    def get_f_du(self, U, t=0):
        '''build dist - vektor for all caf
        '''
        u = U.reshape(self.n_N, self.n_D)
        d_xyz = np.zeros_like(u)
        x = self.get_new_nodes(u)
        dist_arr = np.array([])
        for caf, nodes in self.tf_lst:
            caf.X_arr = x[nodes]
            caf.t = t
            d_arr = caf.d_arr
            dist_arr = np.append(dist_arr, d_arr)
            d_xyz[nodes] = caf.d_arr[:, np.newaxis] * caf.d_xyz_arr

        dist_norm = np.linalg.norm(dist_arr)
        d_xyz[ np.isnan(d_xyz)] = 0.0
        return d_xyz.flatten() / dist_norm

    def get_f_du_t(self, U):
        return self.get_f_du(U, self.t)

    #===========================================================================
    # Equality constraints
    #===========================================================================
    def get_G(self, U, t=0):
        G_lst = [ eqcons.get_G(U, t) for eqcons in self.eqcons_lst ]
        if(G_lst == []):
            return []
        return np.hstack(G_lst)

    def get_G_t(self, U):
        return self.get_G(U, self.t)

    def get_G_du(self, U, t=0):
        G_dx_lst = [ eqcons.get_G_du(U, t) for eqcons in self.eqcons_lst ]
        if(G_dx_lst == []):
            return []
        return np.vstack(G_dx_lst)

    def get_G_du_t(self, U):
        return self.get_G_du(U, self.t)

    #===============================================================================
    # Verification procedures to check the compliance with the constant length criteria.
    #===============================================================================
    def get_new_nodes(self, U):
        '''
            Calculates the lengths of the crease lines.
        '''
        u = U.reshape(self.n_N, self.n_D)
        return self.x_0 + u

    def get_new_vectors(self, U):
        '''
            Calculates the lengths of the crease lines.
        '''
        cX = self.get_new_nodes(U)
        cl = self.L
        return cX[ cl[:, 1] ] - cX[ cl[:, 0] ]

    def get_new_lengths(self, U):
        '''
            Calculates the lengths of the crease lines.
        '''
        cV = self.get_new_vectors(U)
        return np.sqrt(np.sum(cV ** 2, axis=1))

    #===========================================================================
    # Output data
    #===========================================================================

    x_0 = Property
    '''Initial position of all nodes.
    '''
    def _get_x_0(self):
        return self.X_0.reshape(-1, self.n_D)

    v_0 = Property
    ''''Initial crease line vectors.
    '''
    def _get_v_0(self):
        return self.cp.c_vectors

    X_t = Property()
    '''History of nodal positions [time, node*dim]).
    '''
    def _get_X_t(self):
        return self.X_0[np.newaxis, :] + self.U_t

    x_t = Property()
    '''History of nodal positions [time, node, dim].
    '''
    def _get_x_t(self):
        n_t = self.X_t.shape[0]
        return self.X_t.reshape(n_t, -1, self.n_D)

    u_t = Property()
    '''History of nodal positions [time, node, dim].
    '''
    def _get_u_t(self):
        n_t = self.U_t.shape[0]
        return self.U_t.reshape(n_t, -1, self.n_D)

    v_t = Property()
    '''History of crease vectors (Array)
    '''
    def _get_v_t(self):
        i = self.L[:, 0]
        j = self.L[:, 1]
        return self.x_t[:, j] - self.x_t[:, i]

    l_t = Property()
    '''History of crease line lengths (Property(Array)).
    '''
    def _get_l_t(self):
        v = self.v_t ** 2
        return np.sqrt(np.sum(v, axis=2))

