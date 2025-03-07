#include "pattern.h"
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

/******** Generic pattern functions ********/

void pattern_init(Pattern *pat, size_t mem_size) {
  pat->mem_size = mem_size;
  pat->next = NULL;
  pat->meta = NULL;
  pat->free = NULL;
}

void pattern_free(Pattern *pat) {
  if (pat->free != NULL) {
    pat->free(pat->meta);
  }
  if (pat->meta != NULL) {
    free(pat->meta);
  }
}

/******** Random pattern ********/

size_t random_next(void *meta, size_t mem_size) {
  (void)(meta); // Discard unused parameter
  size_t ind = rand() % mem_size;
  return ind;
}

void pattern_random(Pattern *pat) {
  struct timeval time;
  gettimeofday(&time, NULL);
  srand(time.tv_usec);
  pat->next = random_next;
  pat->meta = NULL;
}

/******** Sequential pattern ********/

typedef struct {
  size_t ind;
} Sequential;

size_t sequential_next(void *meta, size_t mem_size) {
  Sequential *m = (Sequential *)meta;
  size_t ind = m->ind % mem_size;
  ++m->ind;
  return ind;
}

void pattern_sequential(Pattern *pat) {
  Sequential *meta = (Sequential *)malloc(sizeof(Sequential));
  meta->ind = 0;

  pat->meta = meta;
  pat->next = sequential_next;
}

/******** Double-sequential pattern ********/

typedef struct {
  size_t ind;
  bool stay;
} Double;

size_t double_next(void *meta, size_t mem_size) {
  Double *m = (Double *)meta;
  size_t ind = m->ind % mem_size;
  if (!m->stay) {
    ++m->ind;
  }
  m->stay = !m->stay;
  return ind;
}

void pattern_double(Pattern *pat) {
  Double *meta = (Double *)malloc(sizeof(Double));
  meta->ind = 0;
  meta->stay = true;

  pat->meta = meta;
  pat->next = double_next;
}

/******** Repeating sequential pattern ********/

typedef struct {
  size_t ind;
  int max_count;
  int cur_count;
} Repeat;

size_t repeat_next(void *meta, size_t mem_size) {
  Repeat *m = (Repeat *)meta;
  size_t ind = m->ind % mem_size;
  if (m->cur_count == m->max_count) {
    m->cur_count = 0;
    ++m->ind;
  }
  ++m->cur_count;
  return ind;
}

void pattern_repeat(Pattern *pat, int repeat_count) {
  Repeat *meta = (Repeat *)malloc(sizeof(Repeat));
  meta->ind = 0;
  meta->max_count = repeat_count;
  meta->cur_count = 0;

  pat->next = repeat_next;
  pat->meta = meta;
}

/******** Zipf-random pattern ********/

typedef struct {
  // First time running flag
  bool first;
  // normalization constant
  double c;
  // pre-calculated sum of probabilities
  double *sum_probs;
  double alpha;
} Zipf;

size_t zipf_next(void *meta, size_t mem_size) {
  Zipf *m = (Zipf *)meta;
  double z;                 // Uniform random number (0 < z < 1)
  int zipf_value = 0;           // Computed exponential value to be returned
  int i;                    // Loop counter
  int low, high, mid;       // Binary-search bounds

  // Compute normalization constant on first call only
  if (m->first) {
    for (i = 1; i <= (int)mem_size; i++)
      m->c = m->c + (1.0 / pow((double)i, m->alpha));
    m->c = 1.0 / m->c;

    m->sum_probs = malloc((mem_size + 1) * sizeof(*m->sum_probs));
    m->sum_probs[0] = 0;
    for (i = 1; i <= (int)mem_size; i++) {
      m->sum_probs[i] = m->sum_probs[i - 1] + m->c / pow((double)i, m->alpha);
    }
    m->first = false;
  }

  // Pull a uniform random number (0 < z < 1)
  do {
    z = drand48();
  } while ((z == 0) || (z == 1));

  // Map z to the value
  low = 1, high = mem_size;
  do {
    mid = floor((low + high) / 2.0);
    if (m->sum_probs[mid] >= z && m->sum_probs[mid - 1] < z) {
      zipf_value = mid;
      break;
    } else if (m->sum_probs[mid] >= z) {
      high = mid - 1;
    } else {
      low = mid + 1;
    }
  } while (low <= high);

  return (zipf_value);
}

void zipf_free(void *meta) {
  Zipf *m = (Zipf *)meta;
  free(m->sum_probs);
}

void pattern_zipf(Pattern *pat, double alpha) {
  Zipf *meta = (Zipf *)malloc(sizeof(Zipf));
  meta->first = true;
  meta->c = 0;
  meta->alpha = alpha;

  pat->meta = meta;
  pat->next = zipf_next;
  pat->free = zipf_free;
}
