use crate::cache::{Cache, CacheLineData, CacheMetadata, CacheTrait};

pub type TreePlruLineMetadata = ();

pub struct TreePlruMetadata {
    /// One bit per tree node.
    /// True points to the right, false points to the left.
    tree: Vec<bool>,
    tree_depth: usize,
    assoc: usize,
}

impl CacheMetadata for TreePlruMetadata {
    fn new(assoc: usize) -> Self {
        let tree_depth = (assoc as f64).log2().round() as usize;
        let num_nodes = assoc - 1;
        let tree = vec![false; num_nodes];

        Self {
            tree_depth,
            tree,
            assoc,
        }
    }
}

impl CacheTrait for Cache<TreePlruLineMetadata, TreePlruMetadata> {
    // When touching a line, go up the hierarchy and turn all directions to point away
    fn touch(&mut self, id: usize, address: usize) {
        let touch_ind;

        if let Some(line_ind) = self.find(id, address) {
            // Found the cache line
            touch_ind = line_ind;
        } else {
            // Didn't find the cache line, evict and replace
            let eviction_candidate = self.evict();
            let cache_line = CacheLineData {
                id,
                addr: address,
                metadata: (),
                cache_metadata: std::marker::PhantomData,
            };
            self.lines[eviction_candidate] = Some(cache_line);
            touch_ind = eviction_candidate;
        }

        // Update all the nodes up the tree to point away from whatever was just touched
        let first_leaf_ind = self.metadata.assoc - 1;
        let leaf_ind = first_leaf_ind + touch_ind;
        let mut trace_ind = leaf_ind;

        while trace_ind >= 1 {
            let is_left_child = trace_ind % 2 == 1;

            // trace to parent
            trace_ind = (trace_ind - 1) / 2;

            // If child is on the left, turn towards the right
            self.metadata.tree[trace_ind] = is_left_child;
        }
    }

    fn evict(&mut self) -> usize {
        let mut trace_ind = 0;
        // Follow the tree to an eviction candidate
        for _ in 0..self.metadata.tree_depth {
            if self.metadata.tree[trace_ind] {
                trace_ind = trace_ind * 2 + 2;
            } else {
                trace_ind = trace_ind * 2 + 1;
            }
        }

        // We have an eviction candidate
        let first_leaf_ind = self.metadata.assoc - 1;
        let leaf_ind = trace_ind - first_leaf_ind;
        self.lines[leaf_ind] = None;
        leaf_ind
    }
}
