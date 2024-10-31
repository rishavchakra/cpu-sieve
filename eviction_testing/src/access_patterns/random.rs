use rand::prelude::*;

use super::{Access, AccessPattern};

pub struct Random {
    id: usize,
    rng: ThreadRng,
    assoc: usize,
    num_addresses: usize,
    num_accesses: usize,
}

impl AccessPattern for Random {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self {
        Self {
            id,
            assoc,
            num_addresses,
            rng: rand::thread_rng(),
            num_accesses: 0,
        }
    }
}

impl Iterator for Random {
    type Item = Access;

    fn next(&mut self) -> Option<Self::Item> {
        let addr = self.rng.gen_range(0..self.num_addresses);
        self.num_accesses += 1;
        Some(Access {
            id: self.id,
            addr,
            num_access: self.num_accesses - 1,
        })
    }
}
