mod double;
mod double_skip;
mod random;
mod sequential;
mod triple;
pub use double::Double;
pub use double_skip::DoubleSkip;
pub use random::Random;
pub use sequential::Sequential;
pub use strum_macros::EnumIter;
pub use triple::Triple;

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
    Triple,
    DoubleSkip,
}

impl AccessPatternType {
    pub fn name(&self) -> String {
        match self {
            AccessPatternType::Sequential => "sequential",
            AccessPatternType::Random => "random",
            AccessPatternType::Double => "double",
            AccessPatternType::Triple => "triple",
            AccessPatternType::DoubleSkip => "double_skip",
        }
        .to_owned()
    }
}
