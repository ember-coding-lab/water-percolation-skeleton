test = {
  'name': 'create_grid',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> from grid import *
          >>> two_by_two = create_grid(2)
          >>> two_by_two
          298fddd718d29636b385f9ddf6d33fc8
          # locked
          >>> len(two_by_two)
          5e152477dfc7d690f4ad6d7de0a8f5c4
          # locked
          >>> three_by_three = create_grid(3)
          >>> three_by_three
          225fd4309484e9e4094e5559f22900e2
          # locked
          >>> len(three_by_three)
          91a2136b7333ddce90a45bd23d166223
          # locked
          >>> one_by_one = create_grid(1)
          >>> one_by_one
          22a1c8293a2c60359175ecf7d5f9fb29
          # locked
          >>> len(one_by_one)
          db4396cc028b0e52681ea670dd918960
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
