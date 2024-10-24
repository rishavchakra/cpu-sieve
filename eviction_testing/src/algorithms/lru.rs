use super::{CacheAddress, CacheLine, CacheSet};

pub struct Lru {
    addr: CacheAddress,
    time_updated: usize,
}

impl CacheLine for Lru {
    fn new(id: usize, addr: usize) -> Self {
        todo!()
    }

    fn get_address(&self) -> usize {
        self.addr.address
    }

    fn get_id(&self) -> usize {
        self.addr.id
    }
}

impl CacheSet<Lru> for Vec<Option<Lru>> {
    fn touch(&mut self, id: usize, address: usize) {
        let update_time = self.iter().fold(0usize, |acc, line| match line {
            Some(l) => std::cmp::max(acc, l.time_updated),
            None => acc,
        });

        if let Some(l) = self.iter_mut().enumerate().find(|line| {
            line.1
                .as_ref()
                .is_some_and(|l| l.addr.id == id && l.addr.address == address)
        }) {
            // If the line is already in the cache, update the updated time
            l.1.as_mut().unwrap().time_updated = update_time + 1;
            return;
        }

        let evict_id = self.evict();
        self[evict_id] = Some(Lru {
            addr: CacheAddress { id, address },
            time_updated: update_time + 1,
        });
    }

    fn evict(&mut self) -> usize {
        if let Some(i) = self.iter().position(|line| line.is_none()) {
            // There's already an empty space, no need to evict
            return i;
        }

        let (evict_id, evict_elem) = self
            .iter_mut()
            .enumerate()
            .min_by_key(|line| line.1.as_ref().unwrap().time_updated)
            .unwrap();

        *evict_elem = None;
        evict_id
    }
}
