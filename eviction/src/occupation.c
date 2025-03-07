#include "algorithms/algorithm.h"
#include "cache.h"
#include "pattern.h"
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEBUG

void debug(const char *, ...);

// Arguments:
// Associativity
// Memory region size
// Replacement policy
// Memory pattern
// Optional other arguments: replacement policy, then memory pattern
int main(int argc, char *argv[]) {
  Cache cache;
  Algorithm algo;
  Pattern pattern;

  if (argc < 3) {
    fprintf(stderr, "Incorrect number of arguments\n");
    exit(1);
  }

  cache_init(&cache, atoi(argv[1]));
  algo_init(&algo, &cache);
  pattern_init(&pattern, atoi(argv[2]));

  // Replacement policy parsing
  int extra_arg_ind = 5;
  const char *r = argv[3];
  if (strcmp(r, "s") == 0) {
    algo_sieve_rand(&algo);
  } else if (strcmp(r, "t") == 0) {
    algo_treeplru_rand(&algo);
  } else if (strcmp(r, "2") == 0) {
    algo_twoq_rand(&algo);
  } else if (strcmp(r, "?") == 0) {
    algo_random(&algo);
  } else {
    fprintf(stderr, "Replacement policy not recognized\n");
    exit(1);
  }

  // Touch pattern parsing
  const char *p = argv[4];
  if (strcmp(p, "s") == 0) {
    pattern_sequential(&pattern);
  } else if (strcmp(p, "d") == 0) {
    pattern_double(&pattern);
  } else if (strcmp(p, "r") == 0) {
    int repeat_count = atoi(argv[extra_arg_ind]);
    pattern_repeat(&pattern, repeat_count);
    ++extra_arg_ind;
  } else if (strcmp(p, "z") == 0) {
    double alpha = strtod(argv[extra_arg_ind], NULL);
    pattern_zipf(&pattern, alpha);
    ++extra_arg_ind;
  } else {
    fprintf(stderr, "Memory access pattern not recognized\n");
    exit(1);
  }

  int i_touch = 0;
  for (; i_touch < 10000; ++i_touch) {
    size_t touch_ind = pattern.next(pattern.meta, pattern.mem_size);
    algo_touch(&algo, USER_ATTACKER, touch_ind);
    if (cache_has_evset(&cache, USER_ATTACKER)) {
      // Attacker has an eviction set
      break;
    }
  }

  // Print the result
  // Later, the result will be collected through stdout
  printf("%d", i_touch);

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
