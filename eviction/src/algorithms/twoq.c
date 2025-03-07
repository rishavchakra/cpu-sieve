#include "../cache.h"
#include "algorithm.h"
#include <stddef.h>

typedef struct {

} QueueItem;

typedef struct {
  int a1_len;
  int am_len;
  QueueItem *a1;
  QueueItem *am;
} Twoq;

void twoq_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {}

int twoq_evict(Cache *cache, void *meta, void *line_meta) {}

void twoq_free(void *meta, void *line_meta) {}

void algo_twoq(Algorithm *algo) {
  algo->func_touch = twoq_touch;
  algo->func_evict = twoq_evict;
  algo->func_free = twoq_free;
}

void algo_twoq_rand(Algorithm *algo) { algo_twoq(algo); }
