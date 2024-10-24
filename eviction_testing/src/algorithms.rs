mod fifo;
mod lru;
mod sieve;
mod treeplru;

pub use fifo::Fifo;
pub use lru::Lru;
pub use sieve::Sieve;

pub trait CacheSet<T>
where
    T: CacheLine,
{
    /// Touches an element and changes metadata according to eviction algorithm
    /// If the element is not present, evicts an element and takes its place
    fn touch(&mut self, id: usize, address: usize);

    /// Evicts an element according to the eviction algorithm
    /// Ensures that there is at least one
    fn evict(&mut self) -> usize;
}

pub trait CacheLine {
    fn new(id: usize, addr: usize) -> Self;
    fn get_address(&self) -> usize;
    fn get_id(&self) -> usize;
}

pub struct CacheAddress {
    id: usize,
    address: usize,
}
