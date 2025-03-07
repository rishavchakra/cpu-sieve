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
  int (*func_evict)(Cache *cache, void *meta, void *line_meta);
  // function run to free algorithm's associated metadata,
  // but should not free meta or line_meta; only subfields within them.
  // nullable: if no subfields need to be freed, this should be null.
  void (*func_free)(void *meta, void *line_meta);
} Algorithm;

void algo_init(Algorithm *algo, Cache *cache);

/// Return: whether the object is present in the cache
/// true: object referenced from cache
/// false: object referenced from DRAM
bool algo_touch(Algorithm *algo, int id, int addr);

void algo_free(Algorithm *algo);

void algo_random(Algorithm *algo);

void algo_treeplru(Algorithm *algo);
void algo_treeplru_rand(Algorithm *algo);

void algo_sieve(Algorithm *algo);
void algo_sieve_rand(Algorithm *algo);

void algo_twoq(Algorithm *algo);
void algo_twoq_rand(Algorithm *algo);

#endif
