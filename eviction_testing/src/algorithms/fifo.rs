use super::{CacheAddress, CacheLine, CacheSet};

pub struct Fifo {
    addr: CacheAddress,
    time_added: usize,
}

impl CacheLine for Fifo {
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

impl CacheSet<Fifo> for Vec<Option<Fifo>> {
    fn touch(&mut self, id: usize, addr: usize) {
        // If the line is already in the cache, no need to do anything
        if let Some(_) = self.iter().find(|line| {
            line.as_ref()
                .is_some_and(|l| l.addr.id == id && l.addr.address == addr)
        }) {
            return;
        }

        let evict_id = self.evict();
        let update_time = self.iter().fold(0usize, |acc, line| match line {
            Some(l) => std::cmp::max(acc, l.time_added),
            None => acc,
        });
        self[evict_id] = Some(Fifo {
            addr: CacheAddress { id, address: addr },
            time_added: update_time + 1,
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
            .min_by_key(|line| line.1.as_ref().unwrap().time_added)
            .unwrap();

        *evict_elem = None;
        evict_id
    }
}
