#include "lib.h"
#include "algorithms/algorithm.h"
#include "pattern.h"
#include <stdio.h>
#include <stdlib.h>

void parse_args(char *argv[], int extra_arg_ind, int algo_ind, int pat_ind,
                Algorithm *algo, Pattern *pat) {
  // Replacement Policy parsing
  const char *r = argv[algo_ind];
  switch (r[0]) {
  case 's': // SIEVE
    algo_sieve_rand(algo);
    break;
  case 't': // TreePLRU
    algo_treeplru_rand(algo);
    break;
  // case '2': // TwoQ, with a1 parameter
  //   algo_twoq_rand(algo, strtod(argv[extra_arg_ind], NULL));
  //   ++extra_arg_ind;
  //   break;
  case '?': // Uniform Random
    algo_random(algo);
    break;
  case '2': // 2Tree
    TwoTreeFlag cold_flag, hot_flag, choice_flag;
    char *splru_args = argv[extra_arg_ind];
    ++extra_arg_ind;
    switch (splru_args[0]) {
    case 'r':
      cold_flag = TREE_COLD_RAND;
      break;
    case 'l':
      cold_flag = TREE_COLD_LRU;
      break;
    case 'f':
      cold_flag = TREE_COLD_FIFO;
    }
    switch (splru_args[1]) {
    case 'r':
      hot_flag = TREE_HOT_RAND;
      break;
    case 'l':
      hot_flag = TREE_HOT_LRU;
      break;
    case 'f':
      hot_flag = TREE_HOT_FIFO;
    }
    switch (splru_args[2]) {
    case 'h':
      choice_flag = CHOOSE_HALF_RAND;
      break;
    case 'q':
      choice_flag = CHOOSE_QUARTER_RAND;
      break;
    case 'e':
      choice_flag = CHOOSE_EIGHTH_RAND;
      break;
    case 'n':
      choice_flag = CHOOSE_NEVER;
      break;
    }

    int flags = cold_flag | hot_flag | choice_flag;
    algo_2tree_rand(algo, flags);
    break;
  case '3': // 3Tree
    algo_3tree(algo);
    break;
  default:
    fprintf(stderr, "ERROR: Replacement policy not recognized\n");
    exit(1);
  }

  // Access Pattern parsing
  const char *p = argv[pat_ind];
  switch (p[0]) {
  case 's': // Sequential
    pattern_sequential(pat);
    break;
  case 'd': // Double
    pattern_double(pat);
    break;
  case 'r': // Repeat
    pattern_repeat(pat, atoi(argv[extra_arg_ind]));
    ++extra_arg_ind;
    break;
  case 'b': // Bounce
    pattern_bounce(pat);
    break;
  case 'z': // Zipf-random
    pattern_zipf(pat, strtod(argv[extra_arg_ind], NULL));
    ++extra_arg_ind;
    break;
  case '?': // Uniform random
    pattern_random(pat);
    break;
  default:
    fprintf(stderr, "ERROR: Memory access pattern not recognized\n");
    exit(1);
  }
}

void debug(const char *str, ...) {
#ifdef DEBUG
  va_list args;
  va_start(args, str);
  printf(str, args);
  va_end(args);
#else
  (void)(str);
#endif
}
