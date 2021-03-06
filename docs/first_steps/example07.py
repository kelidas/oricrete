from oricrete.folding2 import \
    CreasePattern, Lifting, CreasePatternView, \
    CF, x_, y_, z_, t_

cp = CreasePattern(X=[[ 0, 0, 0 ],
                      [ 1, 0, 0 ]],
                   L=[[ 0, 1 ]],
                   )

lift = Lifting(cp=cp,
               n_steps=10,
               dof_constraints=[([(1, 1, 1.0)], 0.0)],
               cf_lst=[(CF(Rf=z_ + 0.2 * ((x_ - 0.5) ** 2 - 0.25)), [0, 1]),
                       (CF(Rf=x_ - 0.5 * y_), [0]), (CF(Rf=x_ - 1.0 + 1. * t_), [1])],
               )

lift.U_0[4] = 0.01

v = CreasePatternView(root=lift.root)
v.configure_traits()
