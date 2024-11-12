use rand::prelude::*;

use crate::cache::{Cache, CacheLineData, CacheLines, CacheMetadata, CacheType};

pub type RandomCache = Cache<RandomLineMetadata, RandomMetadata>;

// No metadata per line for random replacement
pub type RandomLineMetadata = ();

// No cache metadata for random replacement
pub struct RandomMetadata {
    rng: ThreadRng,
}

impl CacheMetadata for RandomMetadata {
    fn new(_: usize) -> Self {
        Self {
            rng: rand::thread_rng(),
        }
    }
}

impl Cache<RandomLineMetadata, RandomMetadata> {
    pub fn new_random(assoc: usize, id: usize) -> Self {
        let mut lines: CacheLines<RandomLineMetadata, RandomMetadata> = Vec::with_capacity(assoc);
        for i in 0..assoc {
            let line = CacheLineData {
                id,
                addr: i,
                metadata: (),
                cache_metadata: std::marker::PhantomData,
            };
            lines.push(Some(line));
        }
        lines.shuffle(&mut rand::thread_rng());
        let cache_metadata = RandomMetadata {
            rng: rand::thread_rng(),
        };
        Self {
            lines,
            metadata: cache_metadata,
        }
    }

    pub fn touch(&mut self, id: usize, address: usize) {
        if let Some(_) = self.find(id, address) {
            return;
        }

        let evict_id = self.evict();
        let cache_line = CacheLineData {
            id,
            addr: address,
            metadata: (),
            cache_metadata: std::marker::PhantomData,
        };
        self.lines[evict_id] = Some(cache_line);
    }

    pub fn evict(&mut self) -> usize {
        if let Some(i) = self.find_empty() {
            return i;
        }

        let evict_id = self.metadata.rng.gen_range(0..self.lines.len());
        self.lines[evict_id] = None;
        evict_id
    }

    pub fn name(&self) -> String {
        "Random".to_string()
    }
}
