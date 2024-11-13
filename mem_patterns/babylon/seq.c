#include <stddef.h>
#include <stdint.h>

#define BUF_LEN 4096
#define NUM_SAMPLES 8192 * 4

int main() {
  // Memory buffer from which we sample
  uint64_t buf[BUF_LEN];

  // Sample from buffer
  size_t i;

#ifndef CONTROL

  for (i = 0; i < NUM_SAMPLES; ++i) {
    // TODO: make sure that this actually accesses the memory
    // access should not be optimized away at any level
    volatile uint64_t access = buf[i % BUF_LEN];
  }

#endif

  return 0;
}
