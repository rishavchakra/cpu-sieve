#include "algorithm.h"
#include "../cache.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

void algo_init(Algorithm *algo, Cache *cache) { algo->cache = cache; }

bool algo_touch(Algorithm *algo, int id, size_t addr) {
  if (cache_has(algo->cache, id, addr)) {
    // Item already in cache, touch it
    int ind = cache_find(algo->cache, id, addr);
    algo->func_touch(algo->cache, algo->meta, algo->line_meta, ind);
    return true;
  } else if (cache_is_full(algo->cache)) {
    // There is no empty space, need to evict something
    size_t evict_ind =
        algo->func_evict(algo->cache, algo->meta, algo->line_meta);
    algo->cache->lines[evict_ind].valid = true;
    algo->cache->lines[evict_ind].id = id;
    algo->cache->lines[evict_ind].addr = addr;
    return false;
  } else {
    // There is empty space in the cache to put this in
    for (int i = 0; i < algo->cache->assoc; ++i) {
      if (!algo->cache->lines[i].valid) {
        algo->cache->lines[i].valid = true;
        algo->cache->lines[i].id = id;
        algo->cache->lines[i].addr = addr;
        break;
      }
    }
    return false;
  }
}

void algo_free(Algorithm *algo) {
  if (algo->func_free != NULL) {
    algo->func_free(algo->meta, algo->line_meta);
  }
  if (algo->meta != NULL) {
    free(algo->meta);
  }
  if (algo->line_meta != NULL) {
    free(algo->line_meta);
  }
}
