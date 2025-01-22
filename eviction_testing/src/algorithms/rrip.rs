use crate::cache::{Cache, CacheLineData, CacheLineMetadata, CacheLines};
use rand::prelude::*;

pub type RripCache<const N: u8> = Cache<RripLineMeta<N>, RripMeta>;

pub struct RripLineMeta<const N: u8> {
    nru: u8,
}

pub type RripMeta = ();

impl<const N: u8> CacheLineMetadata<RripMeta> for RripLineMeta<N> {
    fn new(cache_metadata: &mut RripMeta) -> Self {
        todo!()
    }

    fn touch(&mut self, cache_metadata: &mut RripMeta) {
        todo!()
    }
}

impl<const N: u8> RripCache<N> {
    pub fn new_random(assoc: usize, id: usize) -> Self {
        let mut lines: CacheLines<RripLineMeta<N>, RripMeta> = Vec::with_capacity(assoc);
        let mut rng = rand::thread_rng();
        for i in 0..assoc {
            let line_metadata = RripLineMeta {
                nru: rng.gen_range(0..2u8.pow(N as u32)),
            };
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
            let line = &mut self.lines[line_ind];
            line.as_mut().unwrap().metadata.touch(&mut ());
            return true;
        }

        let evict_id = self.evict();
        let cache_line_metadata = RripLineMeta::new(&mut ());
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

        // RRIP condition: must have at least one with max NRU
        while true {
            let any_nru = self
                .lines
                .iter()
                .any(|l| l.as_ref().unwrap().metadata.nru == 2u8.pow(N as u32) - 1);
            if !any_nru {
                for l in &mut self.lines {
                    let line = l.as_mut().unwrap();
                    line.metadata.nru += 1;
                }
            } else {
                break;
            }
        }

        for (i, l) in &mut self.lines.iter().enumerate() {
            if l.as_ref().unwrap().metadata.nru == 2u8.pow(N as u32 - 1) {
                return i;
            }
        }

        unreachable!("RRIP failed to find an eviction candidate")
    }

    pub fn name(&self) -> String {
        format!("RRIP-{}", N)
    }
}
