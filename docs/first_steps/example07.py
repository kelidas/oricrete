from oricrete.folding2 import CreasePattern, Lifting
from oricrete.folding2.cnstr_control_face import CF, x_, y_, z_, t_

cp = CreasePattern(X=[[ 0, 0, 0 ],
                      [ 1, 0, 0 ]],
                   L=[[ 0, 1 ]],
                   cf_lst=[(CF(Rf=z_ + 0.2 * ((x_ - 0.5) ** 2 - 0.25)), [0, 1]),
                           (CF(Rf=x_ - 0.5 * y_), [0]), (CF(Rf=x_ - 1.0 + 1. * t_), [1])],
                   )

lift = Lifting(cp=cp,
               n_steps=10,
               cnstr_lhs=[[(1, 1, 1.0)]])

lift.u_0[4] = 0.01
print lift.x_t[-1]
lift.show()
