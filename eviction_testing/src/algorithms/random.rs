use rand::prelude::*;

use crate::cache::{Cache, CacheLineData, CacheMetadata, CacheTrait};

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

impl CacheTrait for Cache<RandomLineMetadata, RandomMetadata> {
    fn touch(&mut self, id: usize, address: usize) {
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

    fn evict(&mut self) -> usize {
        if let Some(i) = self.find_empty() {
            return i;
        }

        let evict_id = self.metadata.rng.gen_range(0..self.lines.len());
        self.lines[evict_id] = None;
        evict_id
    }
}
