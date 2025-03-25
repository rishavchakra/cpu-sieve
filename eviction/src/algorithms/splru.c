#include "../cache.h"
#include "algorithm.h"
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

typedef struct SplruTree {
  struct SplruTree *left;
  struct SplruTree *right;
  struct SplruTree *parent;
  bool direction;
} SplruNode;

typedef struct {
  SplruNode *cold;
  SplruNode *hot;
  SplruNode *probation;
  SplruNode **leaf_nodes;
} Splru;

void rec_splru_tree_init(SplruNode *node, size_t cur_depth, size_t ind,
                         SplruNode **node_arr) {
  if (cur_depth == 0) {
    node->left = NULL;
    node->right = NULL;
    node->direction = false;
    node_arr[ind] = node;
    return;
  }
  SplruNode *left = (SplruNode *)malloc(sizeof(SplruNode));
  SplruNode *right = (SplruNode *)malloc(sizeof(SplruNode));
  node->direction = false;
  node->left = left;
  node->right = right;
  left->parent = node;
  right->parent = node;

  rec_splru_tree_init(left, cur_depth + 1, ind * 2, node_arr);
  rec_splru_tree_init(right, cur_depth + 1, ind * 2 + 1, node_arr);
}

void rec_splru_tree_free(SplruNode *node) {
  if (node->left == NULL && node->right == NULL) {
    free(node);
    return;
  }
  rec_splru_tree_free(node->left);
  rec_splru_tree_free(node->right);
  free(node);
}

void algo_split_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {
  Splru *m = (Splru *)meta;
  int flags = *(SplruFlag *)line_meta;

  size_t cold_assoc = cache->assoc / 4;
  size_t hot_ind = ind;

  if (ind < cold_assoc) {
    // Evict something from the hot queue
    // Move cache line from cold to hot queue
    // Including cache data from `cache` object
    // Mark cold queue opening as empty
    size_t evict_ind;
    if (flags & TREE_COLD_LRU || flags & TREE_COLD_FIFO) {
      // Tree-based eviction strategies
      SplruNode *trace_node = m->cold;
      while (trace_node->left != NULL && trace_node->right != NULL) {
        if (trace_node->direction) {
          trace_node = trace_node->right;
          evict_ind = evict_ind * 2 + 1;
        } else {
          trace_node = trace_node->left;
          evict_ind = evict_ind * 2;
        }
      }
    } else {
      // Random eviction
      size_t assoc = cache->assoc;
      size_t quarter_assoc = assoc / 4;
      evict_ind = rand() % quarter_assoc;
    }

    memmove(&cache->lines[evict_ind], &cache->lines[ind], sizeof(CacheLine));
    cache->lines[ind].valid = false;
    hot_ind = evict_ind;
  }
  // Object is now in the hot queue
  // Moved there, if previously in cold queue
  // Already there, if in the hot queue
  // Use touch algorithm in hot queue to mark new element as MRU
  if (flags & TREE_HOT_LRU) {
    SplruNode *leaf = m->leaf_nodes[hot_ind];
    SplruNode *trace = leaf;
    while (trace->parent != NULL) {
      bool is_left_child = trace->parent->left == trace;
      if (is_left_child) {
        trace->parent->direction = true;
      } else {
        trace->parent->direction = false;
      }
      trace = trace->parent;
    }
  } else if (flags & TREE_HOT_FIFO) {
    SplruNode *leaf = m->leaf_nodes[hot_ind];
    SplruNode *trace = leaf;
    while (trace->parent != NULL) {
      bool is_left_child = trace->parent->left == trace;
      if (is_left_child) {
        trace->parent->direction = true;
        break;
      } else {
        trace->parent->direction = false;
      }
      trace = trace->parent;
    }
  }
}

// Random eviction: Randomly evicts from either cold queue or third-quarter
// Deterministic eviction: Evicts from the cold queue, always
size_t algo_splru_evict(Cache *cache, void *meta, void *line_meta) {
  (void)(cache);
  Splru *m = (Splru *)meta;
  int flags = *(int *)line_meta;

  SplruNode *trace_node;
  if (flags & CHOOSE_RAND) {
    if (rand() % 2 == 0) {
      trace_node = m->cold;
    } else {
      trace_node = m->probation;
    }
  } else {
    trace_node = m->cold;
  }

  if (flags & TREE_COLD_LRU || flags & TREE_COLD_FIFO) {
    // Tree-based eviction strategies
    size_t evict_ind = 0;
    while (trace_node->left != NULL && trace_node->right != NULL) {
      if (trace_node->direction) {
        trace_node = trace_node->right;
        evict_ind = evict_ind * 2 + 1;
      } else {
        trace_node = trace_node->left;
        evict_ind = evict_ind * 2;
      }
    }
    return evict_ind;
  } else {
    // Random eviction
    size_t evict_ind = 0;
    while (trace_node->left != NULL && trace_node->right != NULL) {
      if (rand() % 2 == 0) {
        trace_node = trace_node->right;
        evict_ind = evict_ind * 2 + 1;
      } else {
        trace_node = trace_node->left;
        evict_ind = evict_ind * 2;
      }
    }
    return evict_ind;
  }
}

void algo_splru_free(void *meta, void *line_meta) {
  (void)(line_meta);
  Splru *m = (Splru *)meta;
  rec_splru_tree_free(m->cold);
  rec_splru_tree_free(m->hot);
}

void algo_splru(Algorithm *algo, int flags) {
  Splru *meta = (Splru *)malloc(sizeof(Splru));
  // We use the flags as a fake line_meta to simplify the code
  int *flags_line_meta = (int *)malloc(sizeof(int));
  memcpy(flags_line_meta, &flags, sizeof(int));

  int assoc = algo->cache->assoc;
  int log_assoc = (int)round(log2(assoc));
  SplruNode *tree = (SplruNode *)malloc(sizeof(SplruNode));
  SplruNode **leaf_arr = (SplruNode **)malloc(assoc * sizeof(SplruNode *));
  rec_splru_tree_init(tree, log_assoc + 1, 0, leaf_arr);
  SplruNode *first_left = tree->left;
  tree->left = first_left->right;
  meta->probation = first_left->right;
  meta->hot = tree;
  meta->cold = first_left->left;
  free(first_left);

  algo->meta = meta;
  algo->line_meta = flags_line_meta;
  algo->func_touch = algo_split_touch;
  algo->func_evict = algo_splru_evict;
  algo->func_free = algo_splru_free;
}
