project('eviction', 'c', version: '0.1', default_options: ['warning_level=3'])

srcs = [
  'src/cache.c',
  'src/pattern.c',
  'src/algorithms/algorithm.c',
  'src/algorithms/random.c',
  'src/algorithms/sieve.c',
  'src/algorithms/tree_plru.c',
  'src/algorithms/twoq.c',
]

exe = executable('occupation', srcs + 'src/occupation.c', install: true)

test('basic', exe)
