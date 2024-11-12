mod double;
mod random;
mod sequential;
pub use random::Random;
pub use sequential::Sequential;
pub use double::Double;
use strum_macros::EnumIter;

#[derive(Debug)]
pub struct Access {
    pub id: usize,
    pub addr: usize,
    pub num_access: usize,
}

pub trait AccessPattern {
    fn new(id: usize, assoc: usize, num_addresses: usize) -> Self
    where
        Self: Sized;
}

#[derive(EnumIter)]
pub enum AccessPatternType {
    Sequential,
    Random,
    Double,
}

impl AccessPatternType {
    pub fn name(&self) -> String {
        match self {
            AccessPatternType::Sequential => "sequential",
            AccessPatternType::Random => "random",
            AccessPatternType::Double => "double",
        }
        .to_owned()
    }
}
