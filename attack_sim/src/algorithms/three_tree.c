#include "algorithm.h"
#include <math.h>
#include <stdlib.h>

typedef struct {
  bool *cold_tree;
  bool *prob_tree;
  bool *hot_tree;
  int hot_depth;
  union { // Prob. and cold depth are necessarily the same
    int prob_depth;
    int cold_depth;
  };
} ThreeTree;

void threetree_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {
  ThreeTree *m = (ThreeTree *)meta;
  size_t assoc = cache->assoc;
  bool *tree_root;
  size_t trace_ind;
  int tree_depth;
  if (ind < assoc / 4) {
    trace_ind = ind + (assoc / 4) - 1;
    tree_root = m->cold_tree;
    tree_depth = m->cold_depth;
  } else if (ind < assoc / 2) {
    trace_ind = ind - 1;
    tree_root = m->prob_tree;
    tree_depth = m->prob_depth;
  } else {
    trace_ind = ind - 1;
    tree_root = m->hot_tree;
    tree_depth = m->hot_depth;
  }

  for (int i = 0; i < tree_depth; ++i) {
    if (trace_ind % 2 == 0) {
      // Right child
      tree_root[trace_ind] = false;
    } else {
      // Left child
      tree_root[trace_ind] = true;
    }
    trace_ind = (trace_ind - 1) / 2;
  }
}

size_t threetree_evict(Cache *cache, void *meta, void *line_meta) {
  (void)(line_meta);
  ThreeTree *m = (ThreeTree *)meta;

  size_t tree_choice = rand() / 8;
  bool *tree_root;
  int tree_depth;
  if (tree_choice < 5) {
    tree_root = m->cold_tree;
    tree_depth = m->cold_depth;
  } else if (tree_choice < 7) {
    tree_root = m->prob_tree;
    tree_depth = m->prob_depth;
  } else {
    tree_root = m->hot_tree;
    tree_depth = m->hot_depth;
  }

  size_t trace_ind = 0;
  for (int i = 0; i < tree_depth; ++i) {
    if (tree_root[trace_ind]) {
      // Right child
      trace_ind = trace_ind * 2 + 2;
    } else {
      // Left child
      trace_ind = trace_ind * 2 + 1;
    }
  }

  if (tree_choice < 5) {
    int assoc = cache->assoc;
    int quarter_assoc = assoc / 4;
    return trace_ind - (quarter_assoc - 1);
  } else if (tree_choice < 7) {
    return trace_ind + 1;
  } else {
    return trace_ind + 1;
  }
}

void threetree_free(void *m, void *line_meta) {
  (void)(line_meta);
  ThreeTree *meta = (ThreeTree *)m;
  free(meta->cold_tree);
  free(meta->prob_tree);
  free(meta->hot_tree);
}

void algo_3tree(Algorithm *algo) {
  int assoc = algo->cache->assoc;
  int half_assoc = assoc / 2;
  int quarter_assoc = assoc / 4;

  bool *cold_tree = (bool *)malloc((quarter_assoc - 1) * sizeof(bool));
  bool *prob_tree = (bool *)malloc((quarter_assoc - 1) * sizeof(bool));
  bool *hot_tree = (bool *)malloc((half_assoc - 1) * sizeof(bool));
  for (int i = 0; i < half_assoc - 1; ++i) {
    hot_tree[i] = false;
    if (i < quarter_assoc - 1) {
      cold_tree[i] = false;
      prob_tree[i] = false;
    }
  }
  int hot_depth = (int)round(log2(half_assoc)); // 3 for 16-way assoc.
  int cold_depth = hot_depth - 1;               // 2 for 8-way assoc.

  ThreeTree *meta = (ThreeTree *)malloc(sizeof(ThreeTree));
  meta->cold_tree = cold_tree;
  meta->prob_tree = prob_tree;
  meta->hot_tree = hot_tree;
  meta->hot_depth = hot_depth;
  meta->cold_depth = cold_depth;

  algo->meta = meta;
  algo->line_meta = NULL;
  algo->func_evict = threetree_evict;
  algo->func_touch = threetree_touch;
  algo->func_free = threetree_free;
}

void algo_3tree_rand(Algorithm *algo) {
  algo_3tree(algo);
  ThreeTree *meta = (ThreeTree *)algo->meta;
  int half_assoc = algo->cache->assoc / 2;
  int quarter_assoc = half_assoc / 4;
  for (int i = 0; i < half_assoc - 1; ++i) {
    meta->hot_tree[i] = rand() % 2 == 0;
    if (i < quarter_assoc - 1) {
      meta->cold_tree[i] = rand() % 2 == 0;
      meta->prob_tree[i] = rand() % 2 == 0;
    }
  }
}
