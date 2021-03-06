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
# Created on Dec 20, 2011 by: rch

# own Modules
from oricrete.folding import \
    CreasePattern, CF, x_, y_, z_, t_ , \
    CreasePatternView

import numpy as np

if __name__ == '__main__':

    cp = CreasePattern(nodes = [[0, 0, 0]], n_steps = 10)

    cp.cf_lst = [(CF(Rf = z_ - x_ ** 2 - 0), [0]),
                    (CF(Rf = y_ - x_ ** 2 - 0), [0]),
                    (CF(Rf = x_ - t_ - 0), [0])]

    X0 = np.zeros((cp.n_dofs,), dtype = float)

    print 'X ff final', cp.solve(X0)

    cpv = CreasePatternView(data = cp, show_cnstr = True)
    cpv.configure_traits()
