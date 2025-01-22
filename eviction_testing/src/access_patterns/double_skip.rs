use super::{Access, AccessPattern};

pub struct DoubleSkip {
    id: usize,
    cur_pointer: usize,
    _num_addresses: usize,
    assoc: usize,
    odd_addrs: bool,
    cur_is_touched: bool,
    num_accesses: usize,
}

impl AccessPattern for DoubleSkip {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self {
        Self {
            id,
            assoc,
            _num_addresses: num_addresses,
            cur_pointer: 0,
            num_accesses: 0,
            odd_addrs: false,
            cur_is_touched: false,
        }
    }
}

impl Iterator for DoubleSkip {
    type Item = Access;

    fn next(&mut self) -> Option<Self::Item> {
        let access = Access {
            id: self.id,
            addr: self.cur_pointer,
            num_access: self.num_accesses,
        };

        self.num_accesses += 1;

        if self.cur_is_touched {
            self.cur_pointer = self.cur_pointer + 2;
            if self.cur_pointer >= self.assoc {
                // wrap to beginning
                if self.odd_addrs {
                    self.cur_pointer = 1 % self.assoc;
                } else {
                    self.cur_pointer = 0;
                }
                self.odd_addrs = !self.odd_addrs;
            }
            self.cur_is_touched = false;
        } else {
            self.cur_is_touched = true;
        }

        Some(access)
    }
}
