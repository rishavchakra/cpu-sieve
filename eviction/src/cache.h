#ifndef __CACHE_H__
#define __CACHE_H__

#include <stdbool.h>

#define USER_VICTIM 0
#define USER_ATTACKER 1

typedef struct CacheLine {
  bool valid;
  /// The user who touched a cache line
  int id;
  /// The address touched
  int addr;
} CacheLine;

typedef struct Cache {
  int assoc;
  CacheLine *lines;
} Cache;

void cache_init(Cache *cache, int assoc);

void cache_free(Cache *cache);

bool cache_is_full(Cache *cache);

bool cache_has_evset(Cache *cache, int id);

bool cache_has(Cache *cache, int id, int addr);

int cache_find(Cache *cache, int id, int addr);

void cache_line_init(CacheLine *line, int id, int addr, bool valid);

#endif
