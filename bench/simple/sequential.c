#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
int main(int c, char *argv[]) {
  size_t buf_len = 1024 * 16;
  uint64_t *buf = (uint64_t *)malloc(buf_len * sizeof(uint64_t));

  for (int i = 0; i < buf_len; ++i) {
    buf[i] = 0;
  }

  for (int i = 0; i < 1024 * 96; ++i) {
    volatile uint64_t access = buf[i % buf_len];
  }
}
