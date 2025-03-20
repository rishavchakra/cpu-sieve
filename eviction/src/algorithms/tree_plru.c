#include "../cache.h"
#include "algorithm.h"
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
  bool **tree_layers;
  int tree_depth;
} TreePlru;

void treeplru_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {
  (void)(cache);
  (void)(line_meta);
  TreePlru *m = (TreePlru *)meta;
  size_t trace_ind = ind;
  for (int i = m->tree_depth - 1; i >= 0; --i) {
    size_t parent_ind = trace_ind / 2;
    bool is_left_child = parent_ind * 2 == trace_ind;
    if (is_left_child) {
      // Turn the node to point to the right
      m->tree_layers[i][parent_ind] = true;
    } else {
      // Turn the node to point to the left
      m->tree_layers[i][parent_ind] = false;
    }
    trace_ind = parent_ind;
  }
}

size_t treeplru_evict(Cache *cache, void *meta, void *line_meta) {
  (void)(cache);
  (void)(line_meta);
  TreePlru *m = (TreePlru *)meta;
  size_t trace_ind = 0;
  size_t ret;
  for (int i = 0; i < m->tree_depth; ++i) {
    bool direction = m->tree_layers[i][trace_ind];
    if (direction) {
      // Right
      trace_ind = trace_ind * 2 + 1;
    } else {
      // Left
      trace_ind = trace_ind * 2;
    }
  }

  ret = trace_ind;

  // The evicted position should be the MRU
  for (int i = m->tree_depth - 1; i >= 0; --i) {
    size_t parent_ind = trace_ind / 2;
    bool is_left_child = parent_ind * 2 == trace_ind;
    if (is_left_child) {
      // Turn the node to point to the right
      m->tree_layers[i][parent_ind] = true;
    } else {
      // Turn the node to point to the left
      m->tree_layers[i][parent_ind] = false;
    }
    trace_ind = parent_ind;
  }
  return ret;
}

void treeplru_free(void *m, void *line_meta) {
  (void)(line_meta);
  TreePlru *meta = (TreePlru *)m;
  for (int i = 0; i < meta->tree_depth; ++i) {
    free(meta->tree_layers[i]);
  }
}

void algo_treeplru(Algorithm *algo) {
  int assoc = algo->cache->assoc;
  int log_assoc = (int)round(log2(assoc));
  TreePlru *meta = (TreePlru *)malloc(sizeof(TreePlru));

  bool **tree_layers = (bool **)malloc(log_assoc * sizeof(bool *));
  int num_layer_nodes = 1;
  for (int i = 0; i < log_assoc; ++i) {
    tree_layers[i] = (bool *)malloc(num_layer_nodes * sizeof(bool));
    for (int node_i = 0; node_i < num_layer_nodes; ++node_i) {
      tree_layers[i][node_i] = false; // Initialize all arrows to point left
    }
    num_layer_nodes *= 2;
  }
  meta->tree_depth = log_assoc;
  meta->tree_layers = tree_layers;

  algo->meta = (void *)meta;
  algo->line_meta = NULL;
  algo->func_touch = treeplru_touch;
  algo->func_evict = treeplru_evict;
  algo->func_free = treeplru_free;
}

void algo_treeplru_rand(Algorithm *algo) {
  algo_treeplru(algo);
  TreePlru *meta = (TreePlru *)algo->meta;
  int num_layer_nodes = 1;
  for (int i = 0; i < meta->tree_depth; ++i) {
    for (int node_i = 0; node_i < num_layer_nodes; ++node_i) {
      meta->tree_layers[i][node_i] = rand() % 2 == 0;
    }
    num_layer_nodes *= 2;
  }
}
