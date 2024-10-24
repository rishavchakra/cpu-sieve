use rand::{distributions::Uniform, prelude::*};

#[derive(Debug)]
pub struct Access {
    pub id: usize,
    pub addr: usize,
    pub num_access: usize,
}

pub trait AccessPattern {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self;
}

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
        let addr = self.rng.sample(Uniform::new(0, self.num_addresses));
        self.num_accesses += 1;
        Some(Access {
            id: self.id,
            addr,
            num_access: self.num_accesses - 1,
        })
    }
}

pub struct Sequential {
    id: usize,
    cur_pointer: usize,
    num_addresses: usize,
    assoc: usize,
    num_accesses: usize,
}

impl AccessPattern for Sequential {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self {
        Self {
            id,
            assoc,
            num_addresses,
            cur_pointer: 0,
            num_accesses: 0,
        }
    }
}

impl Iterator for Sequential {
    type Item = Access;

    fn next(&mut self) -> Option<Self::Item> {
        let access = Access {
            id: self.id,
            addr: self.cur_pointer,
            num_access: self.num_accesses,
        };
        self.num_accesses += 1;
        self.cur_pointer = (self.cur_pointer + 1) % self.num_addresses;
        Some(access)
    }
}
