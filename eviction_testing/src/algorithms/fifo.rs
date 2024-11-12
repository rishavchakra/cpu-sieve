use crate::cache::{Cache, CacheLineData, CacheLineMetadata, CacheLines, CacheMetadata, CacheType};
use rand::prelude::*;

pub type FifoCache = Cache<FifoLineMetadata, FifoMetadata>;

pub struct FifoLineMetadata {
    time_added: usize,
}

pub struct FifoMetadata {
    time: usize,
}

impl CacheLineMetadata<FifoMetadata> for FifoLineMetadata {
    fn new(cache_metadata: &mut FifoMetadata) -> Self {
        cache_metadata.time += 1;
        FifoLineMetadata {
            time_added: cache_metadata.time,
        }
    }

    fn touch(&mut self, _: &mut FifoMetadata) {
        // No update logic on touch
    }
}

impl CacheMetadata for FifoMetadata {
    fn new(_: usize) -> Self {
        FifoMetadata { time: 0 }
    }
}

impl Cache<FifoLineMetadata, FifoMetadata> {
    pub fn new_random(assoc: usize, id: usize) -> Self {
        let mut lines: CacheLines<FifoLineMetadata, FifoMetadata> = Vec::with_capacity(assoc);
        for i in 0..assoc {
            let line_metadata = FifoLineMetadata { time_added: i };
            let line = CacheLineData {
                id,
                addr: i,
                metadata: line_metadata,
                cache_metadata: std::marker::PhantomData,
            };
            lines.push(Some(line));
        }
        lines.shuffle(&mut rand::thread_rng());
        let cache_metadata = FifoMetadata { time: assoc };
        Self {
            lines,
            metadata: cache_metadata,
        }
    }

    pub fn touch(&mut self, id: usize, address: usize) {
        // If the line is already in the cache, no need to do anything
        if let Some(_) = self.find(id, address) {
            return;
        }

        let evict_id = self.evict();
        let cache_line_metadata = FifoLineMetadata::new(&mut self.metadata);
        let cache_line = CacheLineData {
            id,
            addr: address,
            metadata: cache_line_metadata,
            cache_metadata: std::marker::PhantomData,
        };
        self.lines[evict_id] = Some(cache_line);
    }

    pub fn evict(&mut self) -> usize {
        if let Some(i) = self.find_empty() {
            // There's already an empty space, no need to evict
            return i;
        }

        let (evict_id, evict_elem) = self
            .lines
            .iter_mut()
            .enumerate()
            .min_by_key(|line| line.1.as_ref().unwrap().metadata.time_added)
            .unwrap();

        *evict_elem = None;
        evict_id
    }

    pub fn name(&self) -> String {
        "FIFO".to_string()
    }
}
