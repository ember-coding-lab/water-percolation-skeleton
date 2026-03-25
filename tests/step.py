test = {
  'name': 'step',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> from grid import *
          >>> g1 = [[2, 2, 2],
          ...       [0, 0, 1],
          ...       [0, 0, 1]]
          >>> step(g1)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g1)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g1)
          d2faac6eff76f1e65519262c4b3fbda3
          # locked
          >>> g2 = [[2, 2, 2, 0],
          ...       [1, 1, 1, 0],
          ...       [0, 0, 1, 1],
          ...       [0, 1, 0, 1]]
          >>> step(g2)
          91a2136b7333ddce90a45bd23d166223
          # locked
          >>> step(g2)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g2)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g2)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g2)
          d2faac6eff76f1e65519262c4b3fbda3
          # locked
          >>> g3 = [[2, 0, 0, 0],
          ...       [1, 0, 1, 0],
          ...       [1, 1, 1, 1],
          ...       [0, 1, 1, 0]]
          >>> step(g3)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g3)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g3)
          db4396cc028b0e52681ea670dd918960
          # locked
          >>> step(g3)
          5e152477dfc7d690f4ad6d7de0a8f5c4
          # locked
          >>> step(g3)
          91a2136b7333ddce90a45bd23d166223
          # locked
          >>> step(g3)
          d2faac6eff76f1e65519262c4b3fbda3
          # locked
          """,
          'hidden': False,
          'locked': True,
          'multiline': False
        }
      ],
      'scored': False,
      'setup': '',
      'teardown': '',
      'type': 'doctest'
    }
  ]
}
