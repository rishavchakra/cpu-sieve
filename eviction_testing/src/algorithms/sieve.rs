use crate::cache::{Cache, CacheLineData, CacheLineMetadata, CacheLines};
use rand::prelude::*;

pub type SieveCache = Cache<SieveLineMetadata, SieveMetadata>;

#[derive(Debug)]
pub struct SieveLineMetadata {
    safe: bool,
    stale: bool,
}

pub type SieveMetadata = ();

impl CacheLineMetadata<SieveMetadata> for SieveLineMetadata {
    fn new(_: &mut SieveMetadata) -> Self {
        SieveLineMetadata {
            safe: false,
            stale: true,
        }
    }

    fn touch(&mut self, _: &mut SieveMetadata) {
        self.stale = false;
    }
}

impl Cache<SieveLineMetadata, SieveMetadata> {
    pub fn new_random(assoc: usize, id: usize) -> Self {
        let mut lines: CacheLines<SieveLineMetadata, SieveMetadata> = Vec::with_capacity(assoc);
        let mut rng = rand::thread_rng();
        for i in 0..assoc {
            let line_metadata = SieveLineMetadata {
                safe: rng.gen(),
                stale: rng.gen(),
            };
            let line = CacheLineData {
                id,
                addr: i,
                metadata: line_metadata,
                cache_metadata: std::marker::PhantomData,
            };
            lines.push(Some(line));
        }
        lines.shuffle(&mut rand::thread_rng());
        Self {
            lines,
            metadata: (),
        }
    }

    pub fn touch(&mut self, id: usize, address: usize) -> bool {
        if let Some(line_ind) = self.find(id, address) {
            let line = &mut self.lines[line_ind];
            line.as_mut().unwrap().metadata.touch(&mut ());
            return true;
        }
        let evict_id = self.evict();
        let cache_line_metadata = SieveLineMetadata::new(&mut ());
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
            // There's already an empty space, no need to evict
            return i;
        }

        let all_safe = self.lines.iter().all(|l| l.as_ref().unwrap().metadata.safe);
        let mut all_unsafe_are_visited = true;
        for line in self.lines.iter() {
            let meta = &line.as_ref().unwrap().metadata;
            if !meta.safe && meta.stale {
                all_unsafe_are_visited = false;
            }
        }

        // If all lines are marked safe, reorganize!
        // Any unsafe lines are made safe if visited, so if this is true for all lines then all
        // lines will soon be marked safe. Reorganize in this case too!
        if all_safe || all_unsafe_are_visited {
            for l in &mut self.lines {
                let line = l.as_mut().unwrap();
                if line.metadata.safe {
                    // Move the lines in the safe set to the unsafe set
                    line.metadata.safe = false;
                    // This line isn't needed in the gem5 version but is here
                    // and I think it's making it worse
                    // TODO: look into this
                    line.metadata.stale = true;
                } else {
                    // Mark the lines in the unsafe set as stale
                    line.metadata.stale = true;
                }
            }
        }

        // Now, search for an eviction candidate
        for (idx, l) in &mut self.lines.iter_mut().enumerate() {
            let line = l.as_mut().unwrap();
            if !line.metadata.safe && line.metadata.stale {
                // We found a suitable candidate
                // In the unsafe set and unvisited
                return idx;
            } else if !line.metadata.safe && !line.metadata.stale {
                line.metadata.safe = true;
                line.metadata.stale = true;
            }
        }

        // If we don't find an eviction candidate, something is wrong. It always should
        unreachable!("SIEVE could not find an eviction candidate!")
    }

    pub fn name(&self) -> String {
        "SIEVE".to_string()
    }
}
