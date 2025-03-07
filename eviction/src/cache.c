#include "cache.h"
#include <stdlib.h>

void cache_init(Cache *cache, int assoc) {
  cache->assoc = assoc;
  cache->lines = (CacheLine *)malloc(sizeof(CacheLine) * assoc);
}

void cache_free(Cache *cache) { free(cache->lines); }

bool cache_is_full(Cache *cache) {
  for (int i = 0; i < cache->assoc; ++i) {
    if (!cache->lines[i].valid) {
      return false;
    }
  }
  return true;
}

bool cache_has_evset(Cache *cache, int id) {
  for (int i = 0; i < cache->assoc; ++i) {
    if (!cache->lines[i].valid) {
      return false;
    }
    if (cache->lines[i].id != id) {
      return false;
    }
  }
  return true;
}

bool cache_has(Cache *cache, int id, int addr) {
  for (int i = 0; i < cache->assoc; ++i) {
    if (cache->lines[i].valid && cache->lines[i].id == id &&
        cache->lines[i].addr == addr) {
      return true;
    }
  }
  return false;
}

int cache_find(Cache *cache, int id, int addr) {
  for (int i = 0; i < cache->assoc; ++i) {
    if (cache->lines[i].valid && cache->lines[i].id == id &&
        cache->lines[i].addr == addr) {
      return i;
    }
  }
  return -1;
}

void cache_line_init(CacheLine *line, int id, int addr, bool valid) {
  line->addr = addr;
  line->id = id;
  line->valid = valid;
}
