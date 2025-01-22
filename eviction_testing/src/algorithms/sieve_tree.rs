use crate::cache::{Cache, CacheLineData, CacheLineMetadata, CacheLines, CacheMetadata};
use rand::prelude::*;

pub type SieveTreeCache = Cache<SieveTreeLineMetadata, SieveTreeMetadata>;

#[derive(Debug)]
pub struct SieveTreeLineMetadata {
    stale: bool,
}

#[derive(Debug)]
pub struct SieveTreeMetadata {
    tree: Vec<bool>,
    tree_depth: usize,
    assoc: usize,
    rng: ThreadRng,
}

impl CacheLineMetadata<SieveTreeMetadata> for SieveTreeLineMetadata {
    fn new(_: &mut SieveTreeMetadata) -> Self {
        SieveTreeLineMetadata { stale: true }
    }

    fn touch(&mut self, _: &mut SieveTreeMetadata) {
        self.stale = false;
    }
}

impl CacheMetadata for SieveTreeMetadata {
    fn new(assoc: usize) -> Self {
        let tree_depth = match assoc {
            1 | 2 => 0,
            a => (a as f64).log2().round() as usize - 1,
        };
        // SIEVE is just random for fully/2-way associative caches
        let num_nodes = match assoc {
            1 | 2 => 0,
            a => (a / 2) - 1,
        };
        let tree = vec![false; num_nodes];

        Self {
            tree,
            assoc,
            tree_depth,
            rng: rand::thread_rng(),
        }
    }
}

impl Cache<SieveTreeLineMetadata, SieveTreeMetadata> {
    pub fn new_random(assoc: usize, id: usize) -> Self {
        let mut lines: CacheLines<SieveTreeLineMetadata, SieveTreeMetadata> =
            Vec::with_capacity(assoc);
        let mut rng = rand::thread_rng();

        for i in 0..assoc {
            let line_metadata = SieveTreeLineMetadata { stale: rng.gen() };
            let line = CacheLineData {
                id,
                addr: i,
                metadata: line_metadata,
                cache_metadata: std::marker::PhantomData,
            };
            lines.push(Some(line));
        }
        lines.shuffle(&mut rand::thread_rng());

        let mut tree_metadata = SieveTreeMetadata::new(assoc);

        let mut trace_ind = 0;
        // Assign a random cursor position
        for _ in 0..tree_metadata.tree_depth {
            let choose_right_child = rng.gen();
            if choose_right_child {
                tree_metadata.tree[trace_ind] = true;
                trace_ind = trace_ind * 2 + 2;
            } else {
                trace_ind = trace_ind * 2 + 1;
            }
        }

        Self {
            lines,
            metadata: tree_metadata,
        }
    }

    pub fn touch(&mut self, id: usize, address: usize) -> bool {
        // println!(
        //     "\n\nTouch {}\n\t{:?}\n{:?}",
        //     address,
        //     self.metadata.tree,
        //     self.lines
        //         .iter()
        //         .map(|line| line.as_ref().unwrap().metadata.stale)
        //         .collect::<Vec<bool>>()
        // );
        if let Some(line_ind) = self.find(id, address) {
            let line = &mut self.lines[line_ind];
            line.as_mut().unwrap().metadata.touch(&mut self.metadata);
            return true;
        }

        if self
            .lines
            .iter()
            .all(|line| line.as_ref().is_some_and(|l| !l.metadata.stale))
        {
            self.lines
                .iter_mut()
                .for_each(|line| line.as_mut().unwrap().metadata.stale = true);
        }

        let evict_id = self.evict();
        let cache_line_metadata = SieveTreeLineMetadata::new(&mut self.metadata);
        let cache_line = CacheLineData {
            id,
            addr: address,
            metadata: cache_line_metadata,
            cache_metadata: std::marker::PhantomData,
        };
        self.lines[evict_id] = Some(cache_line);
        // println!(
        //     "Evict {}\n\t{:?}\n{:?}",
        //     evict_id,
        //     self.metadata.tree,
        //     self.lines
        //         .iter()
        //         .map(|line| line.as_ref().unwrap().metadata.stale)
        //         .collect::<Vec<bool>>()
        // );
        false
    }

    pub fn evict(&mut self) -> usize {
        if let Some(i) = self.find_empty() {
            return i;
        }

        match self.metadata.assoc {
            1 => {
                self.lines[0] = None;
                0
            }
            2 => {
                match (
                    self.lines[0].as_ref().unwrap().metadata.stale,
                    self.lines[1].as_ref().unwrap().metadata.stale,
                ) {
                    (false, false) | (true, true) => {
                        let evict_id = self.metadata.rng.gen_range(0..=1);
                        self.lines[evict_id] = None;
                        evict_id
                    }
                    (true, false) => {
                        self.lines[0] = None;
                        0
                    }
                    (false, true) => {
                        self.lines[1] = None;
                        1
                    }
                }
            }
            a => {
                // Trace through the tree to find the cursor
                let mut trace_ind = 0;
                for _ in 0..self.metadata.tree_depth {
                    if self.metadata.tree[trace_ind] {
                        trace_ind = trace_ind * 2 + 2;
                    } else {
                        trace_ind = trace_ind * 2 + 1;
                    }
                }

                let evict_direction;
                let cursor_move;

                let first_leaf_ind = a - 1;
                let left_ind = trace_ind * 2 + 1 - first_leaf_ind;
                let right_ind = trace_ind * 2 + 2 - first_leaf_ind;
                let evict_node_ind;
                let non_evict_node_ind;

                match (
                    self.lines[left_ind].as_ref().unwrap().metadata.stale,
                    self.lines[right_ind].as_ref().unwrap().metadata.stale,
                ) {
                    (false, false) => {
                        evict_direction = self.metadata.rng.gen_bool(0.5);
                        // If neither stale, move on
                        cursor_move = true;
                    }
                    (true, false) => {
                        evict_direction = false;
                        cursor_move = false;
                    }
                    (false, true) => {
                        evict_direction = true;
                        cursor_move = false;
                    }
                    (true, true) => {
                        evict_direction = self.metadata.rng.gen_bool(0.5);
                        // No - I want to stay on this until it's clean
                        cursor_move = false;
                    }
                }

                // We have a pair from which to choose
                if evict_direction {
                    evict_node_ind = trace_ind * 2 + 2;
                    non_evict_node_ind = trace_ind * 2 + 1;
                } else {
                    non_evict_node_ind = trace_ind * 2 + 2;
                    evict_node_ind = trace_ind * 2 + 1;
                }

                let evict_ind = evict_node_ind - first_leaf_ind;
                let _non_evict_ind = non_evict_node_ind - first_leaf_ind;
                self.lines[evict_ind] = None;
                // self.lines[non_evict_ind].as_mut().unwrap().metadata.stale = true;

                // If the cursor should move, move it
                if cursor_move {
                    while trace_ind >= 1 {
                        let is_left_child = trace_ind % 2 == 1;

                        trace_ind = (trace_ind - 1) / 2;

                        if is_left_child {
                            self.metadata.tree[trace_ind] = true;
                            break;
                        } else {
                            self.metadata.tree[trace_ind] = false;
                        }
                    }
                }

                // Return the selected line from earlier
                evict_ind
            }
        }
    }

    pub fn name(&self) -> String {
        "SIEVE-tree".to_owned()
    }
}
