#include "../cache.h"
#include "algorithm.h"
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

typedef struct TreePlruNode {
  struct TreePlruNode *left;
  struct TreePlruNode *right;
  bool direction;
} TreePlruNode;

typedef struct {
  TreePlruNode root;
  int tree_depth;
} TreePlru;

void tree_build_rec(TreePlruNode *root, int depth) {
  if (depth == 0) {
    return;
  }
  TreePlruNode *left = (TreePlruNode *)malloc(sizeof(TreePlruNode));
  TreePlruNode *right = (TreePlruNode *)malloc(sizeof(TreePlruNode));
  root->left = left;
  root->right = right;
  root->direction = false;
  tree_build_rec(left, depth - 1);
  tree_build_rec(right, depth - 1);
}

void tree_rand_rec(TreePlruNode *root, int depth) {
  if (depth == 0) {
    root->left = NULL;
    root->right = NULL;
    root->direction = false;
    return;
  }
  root->direction = rand() % 2 == 0;
  tree_rand_rec(root->left, depth - 1);
  tree_rand_rec(root->right, depth - 1);
}

int tree_trace_rec(TreePlruNode *root, int depth, int trace_ind) {
  if (depth == 0) {
    return trace_ind;
  }
  if (root->direction) {
    return tree_trace_rec(root->right, depth - 1, trace_ind * 2 + 1);
  } else {
    return tree_trace_rec(root->left, depth - 1, trace_ind * 2);
  }
}

void tree_free_rec(TreePlruNode *root, int depth) {
  if (depth == 0 || (root->left == NULL && root->right == NULL)) {
    return;
  }

  tree_free_rec(root->left, depth - 1);
  tree_free_rec(root->right, depth - 1);
  free(root->left);
  free(root->right);
}

void tree_touch_rec(TreePlruNode *root, int depth, int trace_ind, int target) {
  if (depth == 0) {
    return;
  }
}

void tree_touch(Cache *_cache, void *meta, void *_line_meta, size_t ind) {
  (void)(_cache);
  (void)(_line_meta);
  TreePlru *metadata = (TreePlru *)meta;
  tree_touch_rec(&metadata->root, metadata->tree_depth, 0, ind);
}

int tree_evict(Cache *_cache, void *meta, void *line_meta) {
  (void)(_cache);
  TreePlru *metadata = (TreePlru *)meta;
  return tree_trace_rec(&metadata->root, metadata->tree_depth, 0);
}

void tree_free(void *meta, void *_line_meta) {
  (void)(_line_meta);
  tree_free_rec(&((TreePlru *)meta)->root, ((TreePlru *)meta)->tree_depth);
}

void algo_treeplru(Algorithm *algo) {
  int assoc = algo->cache->assoc;
  int log_assoc = (int)round(log2(assoc));
  TreePlru *meta = (TreePlru *)malloc(sizeof(TreePlru));
  meta->tree_depth = log_assoc;
  tree_build_rec(&meta->root, log_assoc);
  algo->meta = (void *)meta;
  algo->line_meta = NULL;
  algo->func_touch = tree_touch;
  algo->func_evict = tree_evict;
  algo->func_free = tree_free;
}

void algo_treeplru_rand(Algorithm *algo) {
  algo_treeplru(algo);
  TreePlruNode tree_root = ((TreePlru *)algo->meta)->root;
  tree_rand_rec(&tree_root, ((TreePlru *)algo->meta)->tree_depth);
}
