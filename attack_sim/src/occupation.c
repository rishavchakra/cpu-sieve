/**
 * This is a script meant to test the ease of occupying a cache set
 * with various eviction algorithms, memory touching patterns, and cache sizes.
 * It assumes a reduced/minimal eviction set and that the attacker knows nothing
 * about the initial cache state.
 */

#include "algorithms/algorithm.h"
#include "cache.h"
#include "lib.h"
#include "pattern.h"
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

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

  cache_init_user(&cache, atoi(argv[1]), USER_VICTIM);
  algo_init(&algo, &cache);
  pattern_init(&pattern, atoi(argv[2]));

  struct timeval time;
  gettimeofday(&time, NULL);
  srand(time.tv_usec);

  parse_args(argv, 5, 3, 4, &algo, &pattern);

  int i_touch = 0;
  for (; i_touch < 100000; ++i_touch) {
    size_t touch_ind = pattern.next(pattern.meta, pattern.mem_size);
    algo_touch(&algo, USER_ATTACKER, touch_ind);
    if (cache_has_evset(&cache, USER_ATTACKER)) {
      break;
    }
  }

  // Print the result
  // Later, the result will be collected through stdout
  printf("%d", i_touch + 1);

  cache_free(&cache);
  algo_free(&algo);
  pattern_free(&pattern);
}
