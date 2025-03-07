#include "algorithm.h"
#include <stddef.h>
#include <stdlib.h>
#include <sys/time.h>

void random_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {
  (void)(cache);
  (void)(meta);
  (void)(line_meta);
  (void)(ind);
}

int random_evict(Cache *cache, void *meta, void *line_meta) {
  (void)(meta);
  (void)(line_meta);
  return rand() % cache->assoc;
}

void algo_random(Algorithm *algo) {
  struct timeval time;
  gettimeofday(&time, NULL);
  srand(time.tv_usec);

  algo->meta = NULL;
  algo->line_meta = NULL;
  algo->func_touch = random_touch;
  algo->func_evict = random_evict;
  algo->func_free = NULL;
}
