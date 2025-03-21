#ifndef __BIN_H__
#define __BIN_H__

#include "algorithms/algorithm.h"
#include "pattern.h"

void parse_args(char *argv[], int extra_arg_ind, int algo_ind, int pat_ind,
                Algorithm *algo, Pattern *pat);

void debug(const char *str, ...);

#endif
