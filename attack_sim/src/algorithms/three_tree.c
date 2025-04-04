#include "../cache.h"
#include "algorithm.h"
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

typedef struct ThreeTreeNode {
  struct ThreeTreeNode *left;
  struct ThreeTreeNode *right;
  struct ThreeTreeNode *parent;
  bool direction;
} ThreeTreeNode;

typedef struct {
  ThreeTreeNode *cold;
  ThreeTreeNode *hot;
  ThreeTreeNode *probation;
  ThreeTreeNode **leaf_nodes;
} ThreeTree;

void rec_3tree_init(ThreeTreeNode *node, size_t cur_depth, size_t ind,
                    ThreeTreeNode **node_arr) {
  if (cur_depth == 0) {
    node->left = NULL;
    node->right = NULL;
    node->direction = false;
    node_arr[ind] = node;
    return;
  }
  ThreeTreeNode *left = (ThreeTreeNode *)malloc(sizeof(ThreeTreeNode));
  ThreeTreeNode *right = (ThreeTreeNode *)malloc(sizeof(ThreeTreeNode));
  node->direction = false;
  node->left = left;
  node->right = right;
  left->parent = node;
  right->parent = node;

  rec_3tree_init(left, cur_depth - 1, ind * 2, node_arr);
  rec_3tree_init(right, cur_depth - 1, ind * 2 + 1, node_arr);
}

void rec_3tree_free(ThreeTreeNode *node) {
  if (node->left == NULL && node->right == NULL) {
    free(node);
    return;
  }
  rec_3tree_free(node->left);
  rec_3tree_free(node->right);
  free(node);
}

void algo_3tree_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {
  ThreeTree *m = (ThreeTree *)meta;
  int flags = *(ThreeTreeFlag *)line_meta;

  size_t cold_assoc = cache->assoc / 4;
  size_t hot_ind = ind;

  if (ind < cold_assoc) {
    // Evict something from the hot queue
    // Move cache line from cold to hot queue
    // Including cache data from `cache` object
    // Mark cold queue opening as empty
    size_t evict_ind = 0;
    if (flags & TREE_COLD_LRU || flags & TREE_COLD_FIFO) {
      // Tree-based eviction strategies
      ThreeTreeNode *trace_node = m->cold;
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

    // Swap the hot obj into the cold queue, cold obj into the hot queue
    // No need to force an unnecessary eviction
    CacheLine temp;
    memcpy(&temp, &cache->lines[evict_ind], sizeof(CacheLine));
    memmove(&cache->lines[evict_ind], &cache->lines[ind], sizeof(CacheLine));
    memcpy(&cache->lines[ind], &temp, sizeof(CacheLine));
    // cache->lines[ind].valid = false;
    hot_ind = evict_ind;
  }
  // Object is now in the hot queue
  // Moved there, if previously in cold queue
  // Already there, if in the hot queue
  // Use touch algorithm in hot queue to mark new element as MRU
  if (flags & TREE_HOT_LRU) {
    ThreeTreeNode *leaf = m->leaf_nodes[hot_ind];
    ThreeTreeNode *trace = leaf;
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
    ThreeTreeNode *leaf = m->leaf_nodes[hot_ind];
    ThreeTreeNode *trace = leaf;
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
// TODO: make new element MRU
size_t algo_3tree_evict(Cache *cache, void *meta, void *line_meta) {
  (void)(cache);
  ThreeTree *m = (ThreeTree *)meta;
  int flags = *(int *)line_meta;

  ThreeTreeNode *trace_node;
  if (flags & CHOOSE_HALF_RAND) {
    if (rand() % 2 == 0) {
      trace_node = m->cold;
    } else {
      trace_node = m->probation;
    }
  } else if (flags & CHOOSE_QUARTER_RAND) {
    if (rand() % 4 == 0) {
      trace_node = m->probation;
    } else {
      trace_node = m->cold;
    }
  } else if (flags & CHOOSE_EIGHTH_RAND) {
    if (rand() % 8 == 0) {
      trace_node = m->probation;
    } else {
      trace_node = m->cold;
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

void algo_3tree_free(void *meta, void *line_meta) {
  (void)(line_meta);
  ThreeTree *m = (ThreeTree *)meta;
  rec_3tree_free(m->cold);
  rec_3tree_free(m->hot);
}

void algo_3tree(Algorithm *algo, int flags) {
  ThreeTree *meta = (ThreeTree *)malloc(sizeof(ThreeTree));
  // We use the flags as a fake line_meta to simplify the code
  int *flags_line_meta = (int *)malloc(sizeof(int));
  memcpy(flags_line_meta, &flags, sizeof(int));

  int assoc = algo->cache->assoc;
  int log_assoc = (int)round(log2(assoc));
  ThreeTreeNode *tree = (ThreeTreeNode *)malloc(sizeof(ThreeTreeNode));
  ThreeTreeNode **leaf_arr =
      (ThreeTreeNode **)malloc(assoc * sizeof(ThreeTreeNode *));
  rec_3tree_init(tree, log_assoc, 0, leaf_arr);
  ThreeTreeNode *first_left = tree->left;
  tree->left = first_left->right;
  meta->probation = first_left->right;
  meta->hot = tree;
  meta->cold = first_left->left;
  meta->cold->parent = NULL;
  meta->leaf_nodes = leaf_arr;
  free(first_left);

  algo->meta = meta;
  algo->line_meta = flags_line_meta;
  algo->func_touch = algo_3tree_touch;
  algo->func_evict = algo_3tree_evict;
  algo->func_free = algo_3tree_free;
}
