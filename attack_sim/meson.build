project('eviction', 'c', version: '0.1', default_options: ['warning_level=3'])

srcs = [
  'src/lib.c',
  'src/cache.c',
  'src/pattern.c',
  'src/algorithms/algorithm.c',
  'src/algorithms/random.c',
  'src/algorithms/sieve.c',
  'src/algorithms/tree_plru.c',
  'src/algorithms/splru.c',
]

executable('occupation', srcs + 'src/occupation.c', install: true)
executable('discovery', srcs + 'src/discovery.c', install: true)
executable('bypass', srcs + 'src/bypass.c', install: true)

# test('basic', occupation_exe)
