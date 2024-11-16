#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#define BUF_LEN 4096
#define NUM_SAMPLES 8192 * 4

typedef uint64_t *ptr_t;

int zipf(double alpha, int n);

int main() {
  size_t i;

  // Memory buffer from which we sample
  uint64_t buf[BUF_LEN];

  // Pointers to items in the buffer
  // helpful for scrambling addresses for random access
  ptr_t ptrs[BUF_LEN];

  size_t samples[NUM_SAMPLES];

  srand(time(NULL));

  // Initialize the pointers array
  for (i = 0; i < BUF_LEN; ++i) {
    ptrs[i] = &buf[i];
  }
  // Scramble the pointers
  // implementation based on https://stackoverflow.com/a/6127606
  for (i = 0; i < BUF_LEN - 1; ++i) {
    size_t j = i + rand() / (RAND_MAX / (BUF_LEN - i) + 1);
    ptr_t t = ptrs[j];
    ptrs[j] = ptrs[i];
    ptrs[i] = t;
  }

  // Generate order of samples
  // Separate from accesses to prevent zipf from interfering with cache
  for (i = 0; i < NUM_SAMPLES; ++i) {
    samples[i] = zipf(1.0, BUF_LEN) - 1;
  }

#ifndef CONTROL

  // Sample from buffer
  for (i = 0; i < NUM_SAMPLES; ++i) {
    size_t cur_sample = samples[i];
    ptr_t ptr_to_access = ptrs[cur_sample];
    // TODO: make sure that this actually accesses the memory
    // access should not be optimized away at any level
    volatile uint64_t access = *ptr_to_access;
  }

#endif

  return 0;
}

// Implementation from https://stackoverflow.com/a/48279287
int zipf(double alpha, int n) {
  static int first = 1;     // Static first time flag
  static double c = 0;      // Normalization constant
  static double *sum_probs; // Pre-calculated sum of probabilities
  double z;                 // Uniform random number (0 < z < 1)
  int zipf_value;           // Computed exponential value to be returned
  int i;                    // Loop counter
  int low, high, mid;       // Binary-search bounds

  // Compute normalization constant on first call only
  if (first == 1) {
    for (i = 1; i <= n; i++)
      c = c + (1.0 / pow((double)i, alpha));
    c = 1.0 / c;

    sum_probs = malloc((n + 1) * sizeof(*sum_probs));
    sum_probs[0] = 0;
    for (i = 1; i <= n; i++) {
      sum_probs[i] = sum_probs[i - 1] + c / pow((double)i, alpha);
    }
    first = 0;
  }

  // Pull a uniform random number (0 < z < 1)
  do {
    z = drand48();
  } while ((z == 0) || (z == 1));

  // Map z to the value
  low = 1, high = n;
  do {
    mid = floor((low + high) / 2.0);
    if (sum_probs[mid] >= z && sum_probs[mid - 1] < z) {
      zipf_value = mid;
      break;
    } else if (sum_probs[mid] >= z) {
      high = mid - 1;
    } else {
      low = mid + 1;
    }
  } while (low <= high);

  return (zipf_value);
}
