use crate::cache::{Cache, CacheLineData, CacheLineMetadata, CacheLines};
use rand::prelude::*;

pub type NruCache = Cache<NruLineMetadata, NruMetadata>;

pub struct NruLineMetadata {
    nru: bool,
}

pub type NruMetadata = ();

impl CacheLineMetadata<NruMetadata> for NruLineMetadata {
    fn new(_: &mut NruMetadata) -> Self {
        Self { nru: false }
    }

    fn touch(&mut self, _: &mut NruMetadata) {
        self.nru = false;
    }
}

impl NruCache {
    pub fn new_random(assoc: usize, id: usize) -> Self {
        let mut lines: CacheLines<NruLineMetadata, NruMetadata> = Vec::with_capacity(assoc);
        let mut rng = rand::thread_rng();
        for i in 0..assoc {
            let line_metadata = NruLineMetadata { nru: rng.gen() };
            let line = CacheLineData {
                id,
                addr: i,
                metadata: line_metadata,
                cache_metadata: std::marker::PhantomData,
            };
            lines.push(Some(line));
        }
        Self {
            lines,
            metadata: (),
        }
    }

    pub fn touch(&mut self, id: usize, address: usize) -> bool {
        if let Some(line_ind) = self.find(id, address) {
            // found correct line
            let line = &mut self.lines[line_ind];
            line.as_mut().unwrap().metadata.touch(&mut ());
            return true;
        }
        let evict_id = self.evict();
        let cache_line_metadata = NruLineMetadata::new(&mut ());
        let cache_line = CacheLineData {
            id,
            addr: address,
            metadata: cache_line_metadata,
            cache_metadata: std::marker::PhantomData,
        };
        self.lines[evict_id] = Some(cache_line);
        false
    }

    pub fn evict(&mut self) -> usize {
        if let Some(i) = self.find_empty() {
            return i;
        }

        let all_recent = self.lines.iter().all(|l| !l.as_ref().unwrap().metadata.nru);
        if all_recent {
            for l in &mut self.lines {
                let line = l.as_mut().unwrap();
                line.metadata.nru = false;
            }
            return 0;
        }

        for (i, l) in &mut self.lines.iter().enumerate() {
            if l.as_ref().unwrap().metadata.nru {
                return i;
            }
        }

        unreachable!("NRU Failed to find an eviction candidate")
    }

    pub fn name(&self) -> String {
        "NRU".to_string()
    }
}
