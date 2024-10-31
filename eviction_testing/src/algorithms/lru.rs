use crate::cache::{Cache, CacheLineData, CacheLineMetadata, CacheMetadata, CacheTrait};

pub type LruCache = Cache<LruLineMetadata, LruMetadata>;

pub struct LruLineMetadata {
    time_updated: usize,
}

pub struct LruMetadata {
    time: usize,
}

impl CacheLineMetadata<LruMetadata> for LruLineMetadata {
    fn new(cache_metadata: &mut LruMetadata) -> Self {
        cache_metadata.time += 1;
        LruLineMetadata {
            time_updated: cache_metadata.time,
        }
    }

    fn touch(&mut self, cache_metadata: &mut LruMetadata) {
        self.time_updated = cache_metadata.time;
        cache_metadata.time += 1;
    }
}

impl CacheMetadata for LruMetadata {
    fn new(_: usize) -> Self {
        LruMetadata { time: 0 }
    }
}

impl CacheTrait for Cache<LruLineMetadata, LruMetadata> {
    fn touch(&mut self, id: usize, address: usize) {
        if let Some(line_ind) = self.find(id, address) {
            let line = &mut self.lines[line_ind];
            line.as_mut().unwrap().metadata.touch(&mut self.metadata);
            return;
        }

        let evict_id = self.evict();
        let cache_line_metadata = LruLineMetadata::new(&mut self.metadata);
        let cache_line = CacheLineData {
            id,
            addr: address,
            metadata: cache_line_metadata,
            cache_metadata: std::marker::PhantomData,
        };
        self.lines[evict_id] = Some(cache_line);
    }

    fn evict(&mut self) -> usize {
        if let Some(i) = self.find_empty() {
            // There's already an empty space, no need to evict
            return i;
        }

        let (evict_id, evict_elem) = self
            .lines
            .iter_mut()
            .enumerate()
            .min_by_key(|line| line.1.as_ref().unwrap().metadata.time_updated)
            .unwrap();

        *evict_elem = None;
        evict_id
    }
}
