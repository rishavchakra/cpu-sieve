mod random;
mod sequential;

use rand::{distributions::Uniform, prelude::*};
pub use random::Random;
pub use sequential::Sequential;

#[derive(Debug)]
pub struct Access {
    pub id: usize,
    pub addr: usize,
    pub num_access: usize,
}

pub trait AccessPattern {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self;
}
