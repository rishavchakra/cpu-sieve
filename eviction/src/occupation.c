/**
 * This is a script meant to test the ease of occupying a cache set
 * with various eviction algorithms, memory touching patterns, and cache sizes.
 * It assumes a reduced/minimal eviction set and that the attacker knows nothing
 * about the initial cache state.
 */

#include "algorithms/algorithm.h"
#include "cache.h"
#include "pattern.h"
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

#define DEBUG

void debug(const char *, ...);

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

  // Replacement policy parsing
  int extra_arg_ind = 5;
  const char *r = argv[3];
  switch (r[0]) {
  case 's': // SIEVE
    algo_sieve_rand(&algo);
    break;
  case 't': // TreePLRU
    algo_treeplru(&algo);
    break;
  case '2': // TwoQ, with a1 parameter
    algo_twoq_rand(&algo, strtod(argv[extra_arg_ind], NULL));
    ++extra_arg_ind;
    break;
  case '?': // Uniform Random
    algo_random(&algo);
    break;
  default:
    fprintf(stderr, "ERROR: Replacement policy not recognized\n");
    exit(1);
  }

  // Touch pattern parsing
  const char *p = argv[4];
  switch (p[0]) {
  case 's': // Sequential
    pattern_sequential(&pattern);
    break;
  case 'd': // Double
    pattern_double(&pattern);
    break;
  case 'r': // Repeat
    pattern_repeat(&pattern, atoi(argv[extra_arg_ind]));
    ++extra_arg_ind;
    break;
  case 'z': // Zipf-random
    pattern_zipf(&pattern, strtod(argv[extra_arg_ind], NULL));
    ++extra_arg_ind;
    break;
  case '?': // Uniform random
    pattern_random(&pattern);
    break;
  default:
    fprintf(stderr, "ERROR: Memory access pattern not recognized\n");
    exit(1);
  }

  int i_touch = 0;
  for (; i_touch < 36; ++i_touch) {
    // for (; i_touch < 10000; ++i_touch) {
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

void debug(const char *str, ...) {
#ifdef DEBUG
  va_list args;
  va_start(args, str);
  printf(str, args);
  va_end(args);
#endif
}
