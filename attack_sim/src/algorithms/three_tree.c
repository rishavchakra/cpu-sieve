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
  if (node->left != NULL && node->right != NULL) {
    rec_3tree_free(node->left);
    rec_3tree_free(node->right);
  }
  free(node);
}

void algo_3tree_touch(Cache *cache, void *meta, void *line_meta, size_t ind) {
  ThreeTree *m = (ThreeTree *)meta;
  int flags = *(ThreeTreeFlag *)line_meta;

  size_t cold_assoc = cache->assoc / 4;
  size_t hot_assoc = cache->assoc - cold_assoc;
  size_t hot_ind = ind;

  if (ind < cold_assoc) {
    // Evict something from the hot queue
    // Move cache line from cold to hot queue
    // Including cache data from `cache` object
    // Mark cold queue opening as empty
    size_t evict_ind = 0;
    // Get hot queue eviction candidate
    if (flags & TREE_HOT_LRU || flags & TREE_HOT_FIFO) {
      // Tree-based eviction strategies
      ThreeTreeNode *trace_node = m->hot;
      while (trace_node->left != NULL && trace_node->right != NULL) {
        if (trace_node->direction) {
          trace_node = trace_node->right;
          evict_ind = evict_ind * 2 + 1;
        } else {
          trace_node = trace_node->left;
          evict_ind = evict_ind * 2;
        }
      }
      // Offset from 0-index to hot tree-index
      if (evict_ind < cold_assoc) {
        // Probation skips one node, so offset this one from 0-indexed to
        // hot-indexed Hot queue already correctly indexed
        evict_ind = evict_ind + cold_assoc;
      }
    } else {
      // Random eviction
      evict_ind = (rand() % hot_assoc) + cold_assoc;
    }

    // Swap the hot obj into the cold queue, cold obj into the hot queue
    // No need to force an unnecessary eviction

    // Swap in the cache structure
    CacheLine temp_line;
    memcpy(&temp_line, &cache->lines[evict_ind], sizeof(CacheLine));
    memmove(&cache->lines[evict_ind], &cache->lines[ind], sizeof(CacheLine));
    memcpy(&cache->lines[ind], &temp_line, sizeof(CacheLine));

    // cache->lines[ind].valid = false;
    hot_ind = evict_ind;
  }
  // Object is now in the hot queue
  // Moved there, if previously in cold queue
  // Already there, if in the hot queue
  // Use touch algorithm in hot queue to mark element as MRU
  if (flags & TREE_HOT_LRU || flags & TREE_HOT_FIFO) {
    // Tree-based touching
    if (flags & TREE_HOT_FIFO && ind >= cold_assoc) {
      // Only has touching logic if newly moved into the hot queue
      return;
    }

    ThreeTreeNode *trace = m->leaf_nodes[hot_ind];
    while (trace->parent != NULL) {
      bool is_left_child = trace->parent->left == trace;
      if (is_left_child) {
        trace->parent->direction = true;
      } else {
        trace->parent->direction = false;
      }
      trace = trace->parent;
    }
  }
  // Random Replacement has no touching logic
}

// Random eviction: Randomly evicts from either cold queue or third-quarter
// Deterministic eviction: Evicts from the cold queue, always
// TODO: make new element MRU
size_t algo_3tree_evict(Cache *cache, void *meta, void *line_meta) {
  (void)(cache);
  ThreeTree *m = (ThreeTree *)meta;
  int flags = *(int *)line_meta;

  ThreeTreeNode *trace_node;
  bool chose_probation = false;
  if (flags & CHOOSE_HALF_RAND) {
    if (rand() % 2 == 0) {
      trace_node = m->cold;
    } else {
      chose_probation = true;
      trace_node = m->probation;
    }
  } else if (flags & CHOOSE_QUARTER_RAND) {
    if (rand() % 4 == 0) {
      chose_probation = true;
      trace_node = m->probation;
    } else {
      trace_node = m->cold;
    }
  } else if (flags & CHOOSE_EIGHTH_RAND) {
    if (rand() % 8 == 0) {
      chose_probation = true;
      trace_node = m->probation;
    } else {
      trace_node = m->cold;
    }
  } else {
    trace_node = m->cold;
  }


  bool cold_tree_repl =
      (flags & TREE_COLD_LRU) > 0 || (flags & TREE_COLD_FIFO) > 0;
  bool hot_tree_repl =
      (flags & TREE_HOT_LRU) > 0 || (flags & TREE_HOT_FIFO) > 0;
  bool tree_repl = (!chose_probation && cold_tree_repl) ||
                   (chose_probation && hot_tree_repl);

  if (tree_repl) {
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

    // New element should be in MRU position, update tree
    while (trace_node->parent != NULL && trace_node->parent != m->hot) {
      bool is_left_child = trace_node->parent->left == trace_node;
      if (is_left_child) {
        trace_node->parent->direction = true;
      } else {
        trace_node->parent->direction = false;
      }
      trace_node = trace_node->parent;
    }

    if (chose_probation) {
      return evict_ind + (cache->assoc / 4);
    } else {
      return evict_ind;
    }
  } else {
    // Random eviction
    if (!chose_probation) {
      // Cold queue
      return rand() % (cache->assoc / 4);
    } else {
      // Probation queue
      return (rand() % (cache->assoc / 4)) + (cache->assoc / 4);
    }
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
  meta->probation->parent = meta->hot;
  meta->leaf_nodes = leaf_arr;
  free(first_left);

  algo->meta = meta;
  algo->line_meta = flags_line_meta;
  algo->func_touch = algo_3tree_touch;
  algo->func_evict = algo_3tree_evict;
  algo->func_free = algo_3tree_free;
}

void rec_3tree_rand(ThreeTreeNode *cur) {
  cur->direction = rand() % 2 == 0;
  if (cur->left == NULL && cur->right == NULL) {
    return;
  }
  rec_3tree_rand(cur->left);
  rec_3tree_rand(cur->right);
}

void algo_3tree_rand(Algorithm *algo, int flags) {
  algo_3tree(algo, flags);
  ThreeTree *meta = (ThreeTree *)algo->meta;
  rec_3tree_rand(meta->hot);
  rec_3tree_rand(meta->cold);
}
