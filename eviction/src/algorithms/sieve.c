#include "../cache.h"
#include "algorithm.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
  bool visited;
} SieveLine;

typedef struct {
  int hand;
} Sieve;

void sieve_touch(Cache *_cache, void *_meta, void *line_meta, size_t ind) {
  (void)(_cache);
  (void)(_meta);
  SieveLine *lines = (SieveLine *)line_meta;
  lines[ind].visited = true;
}

size_t sieve_evict(Cache *cache, void *meta, void *line_meta) {
  Sieve *metadata = (Sieve *)meta;
  SieveLine *line_buf = (SieveLine *)line_meta;
  while (line_buf[metadata->hand].visited) {
    line_buf[metadata->hand].visited = false;
    ++metadata->hand;
    metadata->hand %= cache->assoc;
  }
  for (int i = metadata->hand; i > 0; --i) {
    CacheLine *line_dest = &cache->lines[i];
    const CacheLine *line_src = &cache->lines[i - 1];
    SieveLine *meta_dest = &line_buf[i];
    const SieveLine *meta_src = &line_buf[i - 1];
    memmove(line_dest, line_src, sizeof(CacheLine));
    memmove(meta_dest, meta_src, sizeof(CacheLine));
  }
  // Double check this
  ++metadata->hand;
  metadata->hand %= cache->assoc;
  return 0;
}

void algo_sieve(Algorithm *algo) {
  int assoc = algo->cache->assoc;
  SieveLine *line_buf = (SieveLine *)malloc(assoc * sizeof(SieveLine));
  Sieve *meta = (Sieve *)malloc(sizeof(Sieve));
  meta->hand = 0;

  for (int i = 0; i < assoc; ++i) {
    line_buf[i].visited = false;
  }

  algo->line_meta = (void *)line_buf;
  algo->meta = (void *)meta;
  algo->func_touch = sieve_touch;
  algo->func_evict = sieve_evict;
  algo->func_free = NULL;
}

void algo_sieve_rand(Algorithm *algo) {
  algo_sieve(algo);
  for (int i = 0; i < algo->cache->assoc; ++i) {
    ((SieveLine *)algo->line_meta)[i].visited = rand() % 2 == 0;
  }
}

void algo_sieve_pe(Algorithm *algo) {}

void algo_sieve_pe_rand(Algorithm *algo) {}
