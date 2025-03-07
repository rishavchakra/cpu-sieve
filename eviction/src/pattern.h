#ifndef __PATTERN_H__
#define __PATTERN_H__

#include <stddef.h>

/**
 * A memory access pattern
 */
typedef struct Pattern {
  // The number of possible memory elements to sample from
  // Initialized by the pattern_init function
  size_t mem_size;
  // Initialized by the specific implementations, after pattern_init
  size_t (*next)(void *meta, size_t mem_size);
  // Initialized by the specific implementations, after pattern_init
  void *meta;
  // Optional function to free fields within the metadata.
  // This should not free the meta member variable.
  void (*free)(void *meta);
} Pattern;

// Generic function to initialize a pattern
void pattern_init(Pattern *pat, size_t mem_size);

// Generic function to free a pattern
void pattern_free(Pattern *pat);

// Each index in order, cycling to 0 when it reaches the mem_size
void pattern_sequential(Pattern *pat);

// Like sequential, but each index is accessed twice
// This is the same as pattern_repeat(2)
void pattern_double(Pattern *pat);

// Repeats an index repeat_count times, sequentially and cyclically accessing indices
void pattern_repeat(Pattern *pat, int repeat_count);

// Zipian random distribution with parameter k
void pattern_zipf(Pattern *pat, double alpha);

#endif
