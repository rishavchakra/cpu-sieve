/**
 * This is a script meant to test the ease of reducing a set of addresses
 * into a minimal eviction set for a cache.
 */

#include "algorithms/algorithm.h"
#include "cache.h"
#include "lib.h"
#include "pattern.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * Arguments:
 * Associativity
 * Memory region size
 * Replacement policy
 * Memory pattern
 * Optional other arguments: replacement policy, then memory pattern
 */
int main(int argc, char *argv[]) {
  Cache cache;
  Algorithm algo;
  Pattern pattern;

  if (argc < 5) {
    fprintf(stderr, "ERROR: Incorrect number of arguments\n");
    exit(1);
  }

  cache_init(&cache, atoi(argv[1]));
  algo_init(&algo, &cache);
  pattern_init(&pattern, atoi(argv[2]));

  parse_args(argv, 5, 3, 4, &algo, &pattern);

  // Test eviction set reduction here
  // printf("%d", result);
  cache_free(&cache);
  algo_free(&algo);
  pattern_free(&pattern);
}
