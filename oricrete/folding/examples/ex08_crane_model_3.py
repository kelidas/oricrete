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
# Created on Sep 8, 2011 by: matthias

from etsproxy.mayavi.core.api import PipelineBase
from etsproxy.mayavi.core.ui.api import MayaviScene, SceneEditor, \
    MlabSceneModel
from etsproxy.mayavi.modules.axes import Axes

from etsproxy.traits.api import HasTraits, Range, Instance, on_trait_change, \
    Trait, Property, Constant, DelegatesTo, cached_property, Str, Delegate, \
    Button, Int
from etsproxy.traits.ui.api import View, Item, Group, ButtonEditor
from etsproxy.mayavi import mlab
from etsproxy.mayavi.core.api import Engine
import numpy as np
import sympy as sp
import thread
from oricrete.folding.singularity_finder import SingularityFinder

# own Modules
from oricrete.folding import \
    CreasePattern, RhombusCreasePattern, CreasePatternView, FF, x_, y_, z_, t_

def rhombus_3x1_crane(n_steps = 10, dx = 1.0):
    '''
        This is a first modell of the which should lift the creasepattern.
        It shows a configuration of constrains in which the crane will lift the pattern
        in the expectet form. NOTE: There is no influence of gravity. 
    '''
    
    cp = CreasePattern(n_steps = n_steps, MAX_ITER = 500)
    
    cp.nodes = [[0, 0, 0],  #0
                [0, 1, 0],
                [1, 0, 0],
                [1, 1, 0],
                [2, 0, 0],
                [2, 1, 0],  #5
                [3, 0, 0],
                [3, 1, 0],
                [0, 0.5, 0],
                [3, 0.5, 0],
                [0.5, 0.5, 0],  #10
                [1.5, 0.5, 0],
                [2.5, 0.5, 0],
                [0.5, 0.333, 0],    #13
                [0.5, 0.667, 0],
                [1.5, 0.333, 0],
                [1.5, 0.667, 0],
                [2.5, 0.333, 0],
                [2.5, 0.667, 0],
                [1.5, 0.5, 1.0],
                [0, 0.5, 1],#20
                [3, 0.5, 1],
                [0, 0.333, 1.0],
                [0, 0.667, 1.0],
                [3, 0.333, 1.0],
                [3, 0.667, 1.0],
                [1.5, 0.333, 1.0],
                [1.5, 0.667, 1.0]
                ]
    
    cp.crease_lines = [[0, 2],  #0
                       [0, 8],
                       [0, 10],
                       [1, 3],
                       [1, 8],
                       [1, 10],
                       [2, 4],
                       [2, 10],
                       [2, 11],
                       [3, 5],
                       [3, 10], #10
                       [3, 11],
                       [4, 6],
                       [4, 11],
                       [4, 12],
                       [5, 7],
                       [5, 11],
                       [5, 12],
                       [6, 9],
                       [6, 12],
                       [7, 9],  #20
                       [7, 12],
                       [8, 10],
                       [9, 12],
                       [10, 11],
                       [11, 12],
                       
                       [19, 20],    #26
                       [19, 21],
                       [20, 22],
                       [20, 23],
                       [19, 26],
                       [19, 27],
                       [21, 24],
                       [21, 25],
                       [13, 22],
                       [14, 23],
                       [15, 26],
                       [16, 27],
                       [17, 24],
                       [18, 25],
                      # [20, 8],
                      # [9, 21]
                       ]
    
    cp.facets = [[0, 2, 10],
                 [2, 4, 11],
                 [4, 6, 12],
                 [2, 11, 10],
                 [4, 11, 12],
                 [0, 8, 10],
                 [6, 9, 12],
                 [1, 3, 10],
                 [3, 5, 11],
                 [5, 7, 12],
                 [3, 10, 11],
                 [5, 11, 12],
                 [1, 8, 10],
                 [7, 9, 12]
                 ]
    #cp.line_pts = [[22, 26],
    #               [23, 27]]
    
    cp.grab_pts = [[13, 0],
                   [14, 7],
                   [15, 1],
                   [16, 8],
                   [17, 2],
                   [18, 9]
                   ]
    
    cp.cnstr_lhs = [[(19, 2, 1.0)],
                    [(19, 1, 1.0)],
                    [(19, 0, 1.0)],
                    [(20, 1, 1.0)],
                    [(20, 2, 1.0)],
                    [(21, 1, 1.0)],
                    [(21, 2, 1.0)],
                    [(20, 0, 1.0), (22, 0, -1.0)],
                    [(20, 0, 1.0), (23, 0, -1.0)],
                    [(20, 2, 1.0), (22, 2, -1.0)],
                    [(20, 2, 1.0), (23, 2, -1.0)],
                    [(19, 0, 1.0), (26, 0, -1.0)],
                    [(19, 0, 1.0), (27, 0, -1.0)],
                    [(19, 2, 1.0), (26, 2, -1.0)],
                    [(19, 2, 1.0), (27, 2, -1.0)],
                    [(21, 0, 1.0), (24, 0, -1.0)],
                    [(21, 0, 1.0), (25, 0, -1.0)],
                    [(21, 2, 1.0), (24, 2, -1.0)],
                    [(21, 2, 1.0), (25, 2, -1.0)],
                    [(14, 1, 1.0), (16, 1, -1.0)],
                    
                    #[(8, 2, 1.0)],
                    [(11, 1, 1.0)],
                    #[(9, 2, 1.0)],
                    [(11, 0, 1.0)],
                    [(13, 0, 1.0), (14, 0, -1.0)],
                    [(16, 1, 1.0), (18, 1, -1.0)],
                    [(2, 2, 1.0), (4, 2, -1.0)],
                    #[(13, 2, 1.0), (17, 2, -1.0)],
                    [(13, 1, 1.0), (15, 1, -1.0)]
                    ]
    
    cp.cnstr_rhs = np.zeros((cp.n_dofs,))
    cp.cnstr_rhs[0] = dx
    
    X0 = np.zeros((cp.n_dofs,), dtype = float)
    
    X0[2] = 0.00005
    X0[5] = 0.00005
    X0[20] = 0.00005
    X0[23] = 0.00005
    
    X0[35] = 0.0003
    
    X0[8] = 0.00025
    X0[11] = 0.00025
    X0[14] = 0.00025
    X0[17] = 0.00025
    
    X0[32] = 0.00017
    X0[38] = 0.00017 
    
    X0[41] = 0.00016334
    X0[44] = 0.00016334
    X0[47] = 0.00028335
    X0[50] = 0.00028335
    X0[53] = 0.00016334
    X0[56] = 0.00016334
    X0[59] = 0.00025
    X0[66] = 0.0001
    X0[68] = 0.00016334
    X0[69] = -0.0001
    X0[71] = 0.00016334
    X0[72] = 0.0001
    X0[74] = 0.00016334
    X0[75] = 0.0001
    X0[77] = 0.00016334
    X0[78] = -0.0001
    X0[80] = 0.00016334
    X0[81] = -0.0001
    X0[83] = 0.00016334
#    X0[86] = 0.00025
#    X0[89] = 0.00025
    X0 *= 1
    
    np.set_printoptions(threshold='nan')
    print 'dR', cp.get_dR(X0)
    print 'R', cp.get_R(X0)
   
    cp.set_next_node(X0)

    print 'L_vct', cp.grab_pts_L
    print 'n_dofs', cp.n_dofs
    print 'n_c', cp.n_c
    print 'n_g', cp.n_g
    print 'necessary constraints', cp.n_dofs - cp.n_c - cp.n_g * cp.n_d - cp.n_l * 2
    print 'cnstr', len(cp.cnstr_lhs)
    
    #cp.show_iter = True 
    X = cp.solve(X0)
    #print'Iterationnodes', cp.iteration_nodes
    #cp.get_line_position(0)  
    return cp

def rhombus_3x2_crane(n_steps = 10, dx = 1):
    """
        This example shows a 3x2 rhombus creasepattern.
         
    """
    cpr = RhombusCreasePattern(n_steps = n_steps,
                              L_x = 3,
                              L_y = 2,
                              n_x = 3,
                              n_y = 4,
                              MAX_ITER = 5000)
    
    X_rcp = cpr.generate_X0()
    X_rcp = X_rcp.reshape((-1,3))
    X_rcp[:,2] += -0.1559
   
    cp = CreasePattern(n_steps = n_steps, MAX_ITER = 500)
    
    cp.nodes = cpr.nodes
    
    cp.crease_lines = cpr.crease_lines
    
    cp.facets = cpr.facets
    
    grab_nodes = [[0.5, 0.333, 0],
                  [0.5, 0.667, 0],
                  [0.5, 1.333, 0],
                  [0.5, 1.667, 0],
                  [1.5, 0.333, 0],
                  [1.5, 0.667, 0],
                  [1.5, 1.333, 0],
                  [1.5, 1.667, 0],
                  [2.5, 0.333, 0],
                  [2.5, 0.667, 0],
                  [2.5, 1.333, 0],
                  [2.5, 1.667, 0]]#33
    
    crane_nodes = [[1.5, 0.5, 1.0],#34
                   [0.5, 0.5, 1],
                   [2.5, 0.5, 1],
                   [0.5, 0.333, 1.0],
                   [0.5, 0.667, 1.0],#38
                   [2.5, 0.333, 1.0],
                   [2.5, 0.667, 1.0],
                   [1.5, 0.333, 1.0],
                   [1.5, 0.667, 1.0],
                   
                   [1.5, 1.5, 1.0],#43
                   [0.5, 1.5, 1],
                   [2.5, 1.5, 1],
                   [0.5, 1.333, 1.0],#46
                   [0.5, 1.667, 1.0],
                   [2.5, 1.333, 1.0],
                   [2.5, 1.667, 1.0],
                   [1.5, 1.333, 1.0],
                   [1.5, 1.667, 1.0],#51
                   ]
    
    cp.nodes = np.vstack([cp.nodes,grab_nodes])
    cp.nodes = np.vstack([cp.nodes,crane_nodes])
    
    
    crane_cl = [#crane 1
                [34, 35],#49
                [34, 36],
                [35, 37],
                [35, 38],
                [36, 39],
                [36, 40],
                [34, 41],#55
                [34, 42],
                
                [37, 22],
                [38, 23],#60
                [39, 30],
                [40, 31],
                [41, 26],
                [42, 27],
                #crane 2
                [43, 44],#65
                [43, 45],
                [44, 46],
                [44, 47],
                [45, 48],
                [45, 49],
                [43, 50],
                [43, 51],
                [46, 24],
                [47, 25],
                [48, 32],
                [49, 33],
                [50, 28],
                [51, 29],
                
                ]
    
    cp.crease_lines = np.vstack([cp.crease_lines,crane_cl])
    
    cp.grab_pts = [[22, 0],
                   [23, 14],
                   [26, 2],
                   [27, 16],
                   [30, 4],
                   [31, 18],
                   [24, 1],
                   [25, 15],
                   [28, 3],
                   [29, 17],
                   [32, 5],
                   [33, 19]
                   ]
#    cp.line_pts = [[37, 49],
#                   [38, 50],
#                   [48, 63],
#                   [49, 64]
#                   ]
#    
    
    cnstr_lhs_2 = [[(34, 2, 1.0)],
                    [(34, 0, 1.0)],
#                    [(34, 1, 1.0)],
                    [(34, 2, 1.0), (41, 2, -1.0)],
                    [(34, 2, 1.0), (42, 2, -1.0)],
                    [(34, 2, 1.0), (43, 2, -1.0)],
                    [(34, 0, 1.0), (41, 0, -1.0)],
                    [(34, 0, 1.0), (42, 0, -1.0)],
                    [(35, 2, 1.0), (37, 2, -1.0)],
                    [(35, 2, 1.0), (38, 2, -1.0)],
                    [(35, 0, 1.0), (37, 0, -1.0)],
                    [(35, 0, 1.0), (38, 0, -1.0)],
                    [(36, 2, 1.0), (39, 2, -1.0)],
                    [(36, 2, 1.0), (40, 2, -1.0)],
                    [(36, 0, 1.0), (39, 0, -1.0)],
                    [(36, 0, 1.0), (40, 0, -1.0)],
                    [(35, 2, 1.0)],
                    [(36, 2, 1.0)],
                    [(36, 1, 1.0), (34, 1, -1.0)],
                    [(35, 1, 1.0), (34, 1, -1.0)],
                    
                    [(43, 0, 1.0)],
#                    [(43, 1, 1.0)],
                    [(43, 2, 1.0), (50, 2, -1.0)],
                    [(43, 2, 1.0), (51, 2, -1.0)],
                    [(43, 0, 1.0), (50, 0, -1.0)],
                    [(43, 0, 1.0), (51, 0, -1.0)],
                    [(44, 2, 1.0), (46, 2, -1.0)],
                    [(44, 2, 1.0), (47, 2, -1.0)],
                    [(44, 0, 1.0), (46, 0, -1.0)],
                    [(44, 0, 1.0), (47, 0, -1.0)],
                    [(45, 2, 1.0), (48, 2, -1.0)],
                    [(45, 2, 1.0), (49, 2, -1.0)],
                    [(45, 0, 1.0), (48, 0, -1.0)],
                    [(45, 0, 1.0), (49, 0, -1.0)],
                    [(44, 2, 1.0)],
                    [(45, 2, 1.0)],
                    [(44, 1, 1.0), (43, 1, -1.0)],
                    [(45, 1, 1.0), (43, 1, -1.0)],
                    
                    [(4, 0, 1.0)],
                    [(1, 1, 1.0)],
                    
                    [(22, 1, 1.0), (26, 1, -1.0)],
                    
                    [(3, 2, 1.0), (6, 2, -1.0)],
                    [(23, 1, 1.0), (27, 1, -1.0)],
                    [(27, 1, 1.0), (31, 1, -1.0)],
                    [(22, 0, 1.0), (23, 0, -1.0)],
                    [(34, 1, 1.0), (18, 1, -1.0)],
                    [(34, 1, 1.0), (43, 1, 1.0)]
                    

                    ]
    
    cnstr_lhs_1 = [[(34, 2, 1.0)],
                    [(34, 0, 1.0)],
                    [(34, 1, 1.0)],
                    [(34, 2, 1.0), (41, 2, -1.0)],
                    [(34, 2, 1.0), (42, 2, -1.0)],
                    [(34, 2, 1.0), (43, 2, -1.0)],
                    [(34, 0, 1.0), (41, 0, -1.0)],
                    [(34, 0, 1.0), (42, 0, -1.0)],
                    [(35, 2, 1.0), (37, 2, -1.0)],
                    [(35, 2, 1.0), (38, 2, -1.0)],
                    [(35, 0, 1.0), (37, 0, -1.0)],
                    [(35, 0, 1.0), (38, 0, -1.0)],
                    [(36, 2, 1.0), (39, 2, -1.0)],
                    [(36, 2, 1.0), (40, 2, -1.0)],
                    [(36, 0, 1.0), (39, 0, -1.0)],
                    [(36, 0, 1.0), (40, 0, -1.0)],
                    [(35, 2, 1.0)],
                    [(36, 2, 1.0)],
                    [(36, 1, 1.0)],
                    [(35, 1, 1.0)],
                    
                    [(43, 0, 1.0)],
                    [(43, 1, 1.0), (45, 1, -1.0)],
                    [(43, 2, 1.0), (50, 2, -1.0)],
                    [(43, 2, 1.0), (51, 2, -1.0)],
                    [(43, 0, 1.0), (50, 0, -1.0)],
                    [(43, 0, 1.0), (51, 0, -1.0)],
                    [(44, 2, 1.0), (46, 2, -1.0)],
                    [(44, 2, 1.0), (47, 2, -1.0)],
                    [(44, 0, 1.0), (46, 0, -1.0)],
                    [(44, 0, 1.0), (47, 0, -1.0)],
                    [(45, 2, 1.0), (48, 2, -1.0)],
                    [(45, 2, 1.0), (49, 2, -1.0)],
                    [(45, 0, 1.0), (48, 0, -1.0)],
                    [(45, 0, 1.0), (49, 0, -1.0)],
                    [(44, 2, 1.0)],
                    [(45, 2, 1.0)],
                    [(44, 1, 1.0), (43, 1, -1.0)],
                    [(43, 1, 1.0), (19, 1, -1.0)],
                    
                    #[(35, 1, 1.0), (12, 1, -1.0)],
                    #[(46, 1, 1.0), (13, 1, -1.0)],
                    #[(35, 1, 1.0), (46, 1, 1.0)],
                    #[(36, 1, 1.0), (47, 1, 1.0)],
                    
                    [(4, 0, 1.0)],
                    [(1, 1, 1.0), (10, 1, -1.0)],
                    #[(10, 1, 1.0)],
                    #[(37, 2, 1.0), (48, 2, -1.0)],
                    #[(26, 1, 1.0), (30, 1, -1.0)],
                    #[(0, 1, 1.0), (3, 1, -1.0)],
                    #[(37, 2, 1.0), (38, 2, -1.0)],
                    #[(29, 1, 1.0), (33, 1, -1.0)],
                    [(22, 1, 1.0), (26, 1, -1.0)],
                    #[(22, 0, 1.0), (24, 0, -1.0)],
                    #[(38, 0, 1.0), (49, 0, -1.0)],
                    #[(48, 2, 1.0), (49, 2, -1.0)],
                    #[(3, 2, 1.0), (6, 2, -1.0)],
                    #[(24, 1, 1.0), (28, 1, -1.0)],
                    #[(27, 1, 1.0), (31, 1, -1.0)],
                    [(3, 2, 1.0), (6, 2, -1.0)],
                    #[(3, 1, 1.0), (6, 1, -1.0)],
                    #[(5, 2, 1.0), (8, 2, -1.0)],
                    #[(30, 0, 1.0), (31, 0, -1.0)]
                    #[(30, 0, 1.0), (31, 0, -1.0)],
                    [(22, 0, 1.0), (23, 0, -1.0)]
#                    [(12, 2, 1.0)],
#                    [(13, 0, 1.0)],
#                    [(14, 2, 1.0)],
#                    [(15, 2, 1.0)]
                    ]
    
    cnstr_lhs_3 = [[(34, 2, 1.0)],
                    [(34, 0, 1.0)],
                    [(34, 1, 1.0), (43, 1, 1.0)],
                    [(34, 2, 1.0), (41, 2, -1.0)],
                    [(34, 2, 1.0), (42, 2, -1.0)],
                    #[(34, 2, 1.0), (43, 2, -1.0)],
                    [(34, 0, 1.0), (41, 0, -1.0)],
                    [(34, 0, 1.0), (42, 0, -1.0)],
                    [(35, 2, 1.0), (37, 2, -1.0)],
                    [(35, 2, 1.0), (38, 2, -1.0)],
                    [(35, 0, 1.0), (37, 0, -1.0)],
                    [(35, 0, 1.0), (38, 0, -1.0)],
                    [(36, 2, 1.0), (39, 2, -1.0)],
                    [(36, 2, 1.0), (40, 2, -1.0)],
                    [(36, 0, 1.0), (39, 0, -1.0)],
                    [(36, 0, 1.0), (40, 0, -1.0)],
                    [(35, 2, 1.0)],
                    [(36, 2, 1.0)],
                    [(36, 1, 1.0),(34, 1, -1.0)],
                    [(35, 1, 1.0),(34, 1, -1.0)],
                    
                    [(43, 0, 1.0)],
                    [(43, 1, 1.0), (45, 1, -1.0)],
                    [(43, 2, 1.0), (50, 2, -1.0)],
                    [(43, 2, 1.0), (51, 2, -1.0)],
                    [(43, 0, 1.0), (50, 0, -1.0)],
                    [(43, 0, 1.0), (51, 0, -1.0)],
                    [(44, 2, 1.0), (46, 2, -1.0)],
                    [(44, 2, 1.0), (47, 2, -1.0)],
                    [(44, 0, 1.0), (46, 0, -1.0)],
                    [(44, 0, 1.0), (47, 0, -1.0)],
                    [(45, 2, 1.0), (48, 2, -1.0)],
                    [(45, 2, 1.0), (49, 2, -1.0)],
                    [(45, 0, 1.0), (48, 0, -1.0)],
                    [(45, 0, 1.0), (49, 0, -1.0)],
                    [(44, 2, 1.0)],
                    [(45, 2, 1.0)],
                    [(44, 1, 1.0), (43, 1, -1.0)],
                    [(43, 1, 1.0), (19, 1, -1.0)],
                    
                    #[(35, 1, 1.0), (12, 1, -1.0)],
                    #[(46, 1, 1.0), (13, 1, -1.0)],
                    #[(35, 1, 1.0), (46, 1, 1.0)],
                    #[(36, 1, 1.0), (47, 1, 1.0)],
                    
                    [(4, 0, 1.0)],
                    [(1, 1, 1.0)],
                    #[(10, 1, 1.0)],
                    #[(37, 2, 1.0), (48, 2, -1.0)],
                    #[(26, 1, 1.0), (30, 1, -1.0)],
                    #[(0, 1, 1.0), (3, 1, -1.0)],
                    #[(37, 2, 1.0), (38, 2, -1.0)],
                    #[(29, 1, 1.0), (33, 1, -1.0)],
                    [(22, 1, 1.0), (26, 1, -1.0)],
                    [(22, 0, 1.0), (23, 0, -1.0)],
                    #[(38, 0, 1.0), (49, 0, -1.0)],
                    #[(48, 2, 1.0), (49, 2, -1.0)],
                    #[(3, 2, 1.0), (6, 2, -1.0)],
                    #[(24, 1, 1.0), (28, 1, -1.0)],
                    #[(27, 1, 1.0), (31, 1, -1.0)],
                    [(3, 2, 1.0), (6, 2, -1.0)],
                    #[(3, 1, 1.0), (6, 1, -1.0)],
                    #[(5, 2, 1.0), (8, 2, -1.0)],
                    #[(30, 0, 1.0), (31, 0, -1.0)]
                    #[(30, 0, 1.0), (31, 0, -1.0)],
                    [(22, 0, 1.0), (23, 0, -1.0)]
#                    [(12, 2, 1.0)],
#                    [(13, 0, 1.0)],
#                    [(14, 2, 1.0)],
#                    [(15, 2, 1.0)]
                    ]
    cp.cnstr_lhs = cnstr_lhs_1
    
    cp.cnstr_rhs = np.zeros((cp.n_dofs,))
    cp.cnstr_rhs[0] = dx
    
    
    X_ext = np.zeros((cp.n_dofs - len(X_rcp.reshape((-1,))),), dtype = float)
    X0 = np.hstack([X_rcp.reshape((-1,)), X_ext])
    
    X0[68] = 0.0
    X0[71] = 0.0
    X0[74] = 0.0
    X0[77] = 0.0
    X0[80] = 0.1441
    X0[83] = 0.1441
    X0[86] = 0.1441
    X0[89] = 0.1441
    X0[92] = 0.0
    X0[95] = 0.0
    X0[98] = 0.0
    X0[101] = 0.0
    
    X0[104] = 0.1441
    X0[125] = 0.1441
    X0[128] = 0.1441
    #X0[131] = 0.45
    X0[152] = 0.1441
    X0[155] = 0.1441
    
    X0[132] = 0.1441
    X0[135] = -0.1441
    
    

    
    
    X0 *= 0.1
    #np.set_printoptions(threshold='nan')
    print 'dR', cp.get_dR(X0)
    print 'R', cp.get_R(X0)
#    sf = SingularityFinder()
#    sf.singul_test(cp.get_dR(X0))
    cp.set_next_node(X0)

    print 'L_vct', cp.grab_pts_L
    print 'n_dofs', cp.n_dofs
    print 'n_c', cp.n_c
    print 'n_g', cp.n_g
    print 'necessary constraints', cp.n_dofs - cp.n_c - cp.n_g * 3 - cp.n_l * 2
    print 'cnstr', len(cp.cnstr_lhs)
    
    #cp.show_iter = True    
    X = cp.solve(X0)
    return cp

def rhombus_3x3_crane(n_steps = 10, dx = 0.7):
    """
        This example shows a 3x2 rhombus creasepattern.
         
    """
    cpr = RhombusCreasePattern(n_steps = n_steps,
                              L_x = 3,
                              L_y = 3,
                              n_x = 3,
                              n_y = 6,
                              MAX_ITER = 5000)
    
    X_rcp = cpr.generate_X0()
    X_rcp = X_rcp.reshape((-1,3))
    X_rcp[:,2] += -0.1559
   
    cp = CreasePattern(n_steps = n_steps, MAX_ITER = 500)
    
    cp.nodes = cpr.nodes
    
    cp.crease_lines = cpr.crease_lines
    
    cp.facets = cpr.facets
    
    grab_nodes = [[0.5, 0.333, 0],#31
                  [0.5, 0.667, 0],
                  [0.5, 1.333, 0],
                  [0.5, 1.667, 0],
                  [0.5, 2.333, 0],#35
                  [0.5, 2.667, 0],
                  [1.5, 0.333, 0],
                  [1.5, 0.667, 0],
                  [1.5, 1.333, 0],
                  [1.5, 1.667, 0],
                  [1.5, 2.333, 0],
                  [1.5, 2.667, 0],
                  [2.5, 0.333, 0],
                  [2.5, 0.667, 0],
                  [2.5, 1.333, 0],#45
                  [2.5, 1.667, 0],
                  [2.5, 2.333, 0],
                  [2.5, 2.667, 0]]#48
    
    crane_nodes = [[1.5, 0.5, 1.0],#49
                   [0.5, 0.5, 1],
                   [2.5, 0.5, 1],
                   [0.5, 0.333, 1.0],
                   [0.5, 0.667, 1.0],
                   [2.5, 0.333, 1.0],
                   [2.5, 0.667, 1.0],#55
                   [1.5, 0.333, 1.0],
                   [1.5, 0.667, 1.0],
                   
                   [1.5, 1.5, 1.0],
                   [0.5, 1.5, 1],
                   [2.5, 1.5, 1],#60
                   [0.5, 1.333, 1.0],
                   [0.5, 1.667, 1.0],
                   [2.5, 1.333, 1.0],
                   [2.5, 1.667, 1.0],
                   [1.5, 1.333, 1.0],#65
                   [1.5, 1.667, 1.0],
                   
                   [1.5, 2.5, 1.0],
                   [0.5, 2.5, 1],
                   [2.5, 2.5, 1],
                   [0.5, 2.333, 1.0],#70
                   [0.5, 2.667, 1.0],
                   [2.5, 2.333, 1.0],
                   [2.5, 2.667, 1.0],
                   [1.5, 2.333, 1.0],
                   [1.5, 2.667, 1.0],#75
                   ]
    
    cp.nodes = np.vstack([cp.nodes,grab_nodes])
    cp.nodes = np.vstack([cp.nodes,crane_nodes])
    
    
    crane_cl = [#crane 1
                [49, 50],#72
                [49, 51],
                [50, 52],
                [50, 53],
                [51, 54],
                [51, 55],
                [49, 56],
                [49, 57],
                
                [52, 31],
                [53, 32],
                [54, 43],
                [55, 44],
                [56, 37],
                [57, 38],
                #crane 2
                [58, 59],
                [58, 60],
                [59, 61],
                [59, 62],
                [60, 63],
                [60, 64],
                [58, 65],
                [58, 66],
                
                [61, 33],
                [62, 34],
                [63, 45],
                [64, 46],
                [65, 39],
                [66, 40],
                
                #crane 3
                [67, 68],
                [67, 69],
                [68, 70],
                [68, 71],
                [69, 72],
                [69, 73],
                [67, 74],
                [67, 75],
                
                [70, 35],
                [71, 36],
                [72, 47],
                [73, 48],
                [74, 41],
                [75, 42],
                
                ]
    
    cp.crease_lines = np.vstack([cp.crease_lines,crane_cl])
    
    cp.grab_pts = [[31, 0],
                   [32, 21],
                   [33, 1],
                   [34, 22],
                   [35, 2],
                   [36, 23],
                   [37, 3],
                   [38, 24],
                   [39, 4],
                   [40, 25],
                   [41, 5],
                   [42, 26],
                   [43, 6],
                   [44, 27],
                   [45, 7],
                   [46, 28],
                   [47, 8],
                   [48, 29]
                   ]
   
    
    
    
    cnstr_lhs_3 = [[(49, 2, 1.0)],
                    [(49, 0, 1.0)],
                    [(49, 1, 1.0), (67, 1, 1.0)],
                    [(49, 2, 1.0), (58, 2, -1.0)],
                    [(49, 2, 1.0), (67, 2, -1.0)],
                    [(49, 2, 1.0), (56, 2, -1.0)],
                    [(49, 2, 1.0), (57, 2, -1.0)],
                    [(49, 0, 1.0), (56, 0, -1.0)],
                    [(49, 0, 1.0), (57, 0, -1.0)],
                    [(50, 2, 1.0), (52, 2, -1.0)],
                    [(50, 2, 1.0), (53, 2, -1.0)],
                    [(50, 0, 1.0), (52, 0, -1.0)],
                    [(50, 0, 1.0), (53, 0, -1.0)],
                    [(51, 2, 1.0), (54, 2, -1.0)],
                    [(51, 2, 1.0), (55, 2, -1.0)],
                    [(51, 0, 1.0), (54, 0, -1.0)],
                    [(51, 0, 1.0), (55, 0, -1.0)],
                    [(50, 2, 1.0)],
                    [(51, 2, 1.0)],
                    [(50, 1, 1.0),(49, 1, -1.0)],
                    [(51, 1, 1.0),(49, 1, -1.0)],
                    
                    [(58, 0, 1.0)],
                    [(58, 2, 1.0), (65, 2, -1.0)],
                    [(58, 2, 1.0), (66, 2, -1.0)],
                    [(58, 0, 1.0), (65, 0, -1.0)],
                    [(58, 0, 1.0), (66, 0, -1.0)],
                    [(59, 2, 1.0), (61, 2, -1.0)],
                    [(59, 2, 1.0), (62, 2, -1.0)],
                    [(59, 0, 1.0), (61, 0, -1.0)],
                    [(59, 0, 1.0), (62, 0, -1.0)],
                    [(60, 2, 1.0), (63, 2, -1.0)],
                    [(60, 2, 1.0), (64, 2, -1.0)],
                    [(60, 0, 1.0), (63, 0, -1.0)],
                    [(60, 0, 1.0), (64, 0, -1.0)],
                    [(59, 2, 1.0)],
                    [(60, 2, 1.0)],
                    [(59, 1, 1.0)],
                    [(60, 1, 1.0)],
                    [(58, 1, 1.0)],
                    
                    [(67, 0, 1.0)],
                    [(67, 2, 1.0), (74, 2, -1.0)],
                    [(67, 2, 1.0), (75, 2, -1.0)],
                    [(67, 0, 1.0), (74, 0, -1.0)],
                    [(67, 0, 1.0), (75, 0, -1.0)],
                    [(68, 2, 1.0), (70, 2, -1.0)],
                    [(68, 2, 1.0), (71, 2, -1.0)],
                    [(68, 0, 1.0), (70, 0, -1.0)],
                    [(68, 0, 1.0), (71, 0, -1.0)],
                    [(69, 2, 1.0), (72, 2, -1.0)],
                    [(69, 2, 1.0), (73, 2, -1.0)],
                    [(69, 0, 1.0), (72, 0, -1.0)],
                    [(69, 0, 1.0), (73, 0, -1.0)],
                    [(68, 2, 1.0)],
                    [(69, 2, 1.0)],
                    [(67, 1, 1.0), (27, 1, -1.0)],
                    [(68, 1, 1.0), (67, 1, -1.0)],
                    [(69, 1, 1.0), (67, 1, -1.0)],
                    
                    #[(35, 1, 1.0), (12, 1, -1.0)],
                    #[(46, 1, 1.0), (13, 1, -1.0)],
                    #[(35, 1, 1.0), (46, 1, 1.0)],
                    #[(36, 1, 1.0), (47, 1, 1.0)],
                    
                    [(25, 0, 1.0)],
                    [(17, 1, 1.0)],
                    #[(10, 1, 1.0)],
                    #[(37, 2, 1.0), (48, 2, -1.0)],
                    #[(26, 1, 1.0), (30, 1, -1.0)],
                    #[(0, 1, 1.0), (3, 1, -1.0)],
                    #[(37, 2, 1.0), (38, 2, -1.0)],
                    #[(29, 1, 1.0), (33, 1, -1.0)],
                    #[(31, 1, 1.0), (37, 1, -1.0)],
                    #[(7, 2, 1.0), (11, 2, -1.0)],
                    #[(22, 0, 1.0), (24, 0, -1.0)],
                    #[(38, 0, 1.0), (49, 0, -1.0)],
                    #[(48, 2, 1.0), (49, 2, -1.0)],
                    #[(3, 2, 1.0), (6, 2, -1.0)],
                    #[(24, 1, 1.0), (28, 1, -1.0)],
                    #[(27, 1, 1.0), (31, 1, -1.0)],
                    [(4, 2, 1.0), (8, 2, -1.0)],
                    #[(3, 1, 1.0), (6, 1, -1.0)],
                    #[(5, 2, 1.0), (8, 2, -1.0)],
                    #[(30, 0, 1.0), (31, 0, -1.0)]
                    #[(30, 0, 1.0), (31, 0, -1.0)],
                    #[(31, 0, 1.0), (32, 0, -1.0)]
#                    [(12, 2, 1.0)],
#                    [(13, 0, 1.0)],
#                    [(14, 2, 1.0)],
#                    [(15, 2, 1.0)]
                    ]
    cp.cnstr_lhs = cnstr_lhs_3
    
    cp.cnstr_rhs = np.zeros((cp.n_dofs,))
    cp.cnstr_rhs[0] = dx
    
    
    X_ext = np.zeros((cp.n_dofs - len(X_rcp.reshape((-1,))),), dtype = float)
    X0 = np.hstack([X_rcp.reshape((-1,)), X_ext])
    
    
    X0[113] = 0.1441
    X0[116] = 0.1441
    X0[119] = 0.1441
    X0[122] = 0.1441
    X0[125] = 0.1441
    X0[128] = 0.1441
    
    X0[149] = 0.1441
    X0[176] = 0.1441
    X0[203] = 0.1441
    #X0[131] = 0.45
    #X0[152] = 0.1441
    #X0[155] = 0.1441
    
   # X0[132] = 0.1441
    #X0[135] = -0.1441
    
    

    
    
    X0 *= 0.1
    #np.set_printoptions(threshold='nan')
    print 'dR', cp.get_dR(X0)
    print 'R', cp.get_R(X0)
    
    cp.set_next_node(X0)

    print 'L_vct', cp.grab_pts_L
    print 'n_dofs', cp.n_dofs
    print 'n_c', cp.n_c
    print 'n_g', cp.n_g
    print 'necessary constraints', cp.n_dofs - cp.n_c - cp.n_g * 3 - cp.n_l * 2
    print 'cnstr', len(cp.cnstr_lhs)
    
    #cp.show_iter = True    
    X = cp.solve(X0)
    return cp

if __name__ == '__main__':

#    cp = rhombus_3x1_crane(n_steps = 80)
    cp = rhombus_3x2_crane(n_steps = 80)
#    cp = rhombus_3x3_crane(n_steps = 80)


    # initialise View
    
    cpv = CreasePatternView(data = cp, show_cnstr = True)
    
    cpv.configure_traits()