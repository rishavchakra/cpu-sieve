#ifndef __ALGORITHM_H__
#define __ALGORITHM_H__

#include "../cache.h"
#include <stdbool.h>
#include <stddef.h>

/**
 * A cache eviction algorithm
 */
typedef struct Algorithm {
  // The associated cache
  Cache *cache;
  // The cache metadata
  void *meta;
  // The cache line metadata array
  void *line_meta;
  // function run when an existing cache object is touched
  // ind: index of cache object in cache array
  void (*func_touch)(Cache *cache, void *meta, void *line_meta, size_t ind);
  // function run when space needs to be made for a new cache object
  // return: index of the freed space
  size_t (*func_evict)(Cache *cache, void *meta, void *line_meta);
  // function run to free algorithm's associated metadata,
  // but should not free meta or line_meta; only subfields within them.
  // nullable: if no subfields need to be freed, this should be null.
  void (*func_free)(void *meta, void *line_meta);
} Algorithm;

void algo_init(Algorithm *algo, Cache *cache);

/// Return: whether the object is present in the cache
/// true: object referenced from cache
/// false: object referenced from DRAM
bool algo_touch(Algorithm *algo, int id, size_t addr);

void algo_free(Algorithm *algo);

void algo_random(Algorithm *algo);

void algo_treeplru(Algorithm *algo);
void algo_treeplru_rand(Algorithm *algo);

// SIEVE and variations
void algo_sieve(Algorithm *algo);
void algo_sieve_rand(Algorithm *algo);

void algo_sieve_pe(Algorithm *algo);
void algo_sieve_pe_rand(Algorithm *algo);

// TwoQ and variations
void algo_twoq(Algorithm *algo, double a1_len);
void algo_twoq_rand(Algorithm *algo, double a1_len);

void algo_twoq_tree_single(Algorithm *algo);
void algo_twoq_tree_single_rand(Algorithm *algo);

void algo_twoq_tree_double(Algorithm *algo);
void algo_twoq_tree_double_rand(Algorithm *algo);

typedef enum {
  TREE_HOT_RAND = 1 << 0,
  TREE_HOT_LRU = 1 << 1,
  TREE_HOT_FIFO = 1 << 2,
  TREE_COLD_RAND = 1 << 3,
  TREE_COLD_LRU = 1 << 4,
  TREE_COLD_FIFO = 1 << 5,
  CHOOSE_NEVER = 1 << 6,
  CHOOSE_HALF_RAND = 1 << 7,
  CHOOSE_QUARTER_RAND = 1 << 8,
  CHOOSE_EIGHTH_RAND = 1 << 9,
} SplruFlag;

void algo_splru(Algorithm *, int flags);

#endif
