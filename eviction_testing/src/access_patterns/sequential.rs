use super::{Access, AccessPattern};

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
