use super::{Access, AccessPattern};

pub struct Triple {
    id: usize,
    cur_pointer: usize,
    touch_num: usize,
    num_addresses: usize,
    _assoc: usize,
    num_accesses: usize,
}

impl AccessPattern for Triple {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self {
        Self {
            id,
            _assoc: assoc,
            num_addresses,
            cur_pointer: 0,
            touch_num: 0,
            num_accesses: 0,
        }
    }
}

impl Iterator for Triple {
    type Item = Access;

    fn next(&mut self) -> Option<Self::Item> {
        let access = Access {
            id: self.id,
            addr: self.cur_pointer,
            num_access: self.num_accesses,
        };
        self.num_accesses += 1;
        if self.touch_num == 2 {
            self.cur_pointer = (self.cur_pointer + 1) % self.num_addresses;
            self.touch_num = 0;
        } else {
            self.touch_num += 1;
        }
        Some(access)
    }
}
