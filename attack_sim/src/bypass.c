/**
 * This is a script meant to test the ease of bypassing the cache
 * and forcing a DRAM hit. This is meant to simulate Rowhammer-style
 * attacks that require repeated cache accesses.
 * It assumes that the attacker knows nothing about the initial cache state.
 */

#include "lib.h"
#include "src/algorithms/algorithm.h"
#include "src/cache.h"
#include "src/pattern.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>

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

  /* Testing section */
  // The number of DRAM hits
  int num_hits = 0;

  for (int i_touch = 0; i_touch < 1000; ++i_touch) {
    size_t touch_ind = pattern.next(pattern.meta, pattern.mem_size);
    bool obj_in_cache = algo_touch(&algo, USER_ATTACKER, touch_ind);
    if (obj_in_cache) {
      ++num_hits;
    }
  }

  // This result will be collected through stdout
  printf("%d", num_hits);

  cache_free(&cache);
  algo_free(&algo);
  pattern_free(&pattern);
}
