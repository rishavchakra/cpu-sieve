use super::{Access, AccessPattern};

pub struct Double {
    id: usize,
    cur_pointer: usize,
    cur_is_touched: bool,
    num_addresses: usize,
    assoc: usize,
    num_accesses: usize,
}

impl AccessPattern for Double {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self {
        Self {
            id,
            assoc,
            num_addresses,
            cur_pointer: 0,
            cur_is_touched: false,
            num_accesses: 0,
        }
    }
}

impl Iterator for Double {
    type Item = Access;

    fn next(&mut self) -> Option<Self::Item> {
        let access = Access {
            id: self.id,
            addr: self.cur_pointer,
            num_access: self.num_accesses,
        };
        self.num_accesses += 1;
        if self.cur_is_touched {
            self.cur_pointer = (self.cur_pointer + 1) % self.num_addresses;
            self.cur_is_touched = false;
        } else {
            self.cur_is_touched = true;
        }
        Some(access)
    }
}
