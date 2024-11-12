use std::marker::PhantomData;

use crate::algorithms::{FifoCache, LruCache, RandomCache, SieveCache, TreePlruCache};

#[derive(Debug)]
pub struct CacheLineData<T, S>
where
    T: CacheLineMetadata<S>,
{
    pub id: usize,
    pub addr: usize,
    pub metadata: T,
    pub cache_metadata: PhantomData<S>,
}

pub type CacheLines<T, S> = Vec<Option<CacheLineData<T, S>>>;

pub struct Cache<T, S>
where
    T: CacheLineMetadata<S>,
    S: CacheMetadata,
{
    pub lines: CacheLines<T, S>,
    pub metadata: S,
}

pub enum CacheType {
    Fifo(FifoCache),
    Lru(LruCache),
    Sieve(SieveCache),
    Random(RandomCache),
    TreePlru(TreePlruCache),
}

pub trait CacheLineMetadata<S> {
    fn new(cache_metadata: &mut S) -> Self;

    fn touch(&mut self, cache_metadata: &mut S);
}

pub trait CacheMetadata {
    fn new(assoc: usize) -> Self;
}

impl CacheType {
    pub fn touch(&mut self, id: usize, address: usize) {
        match self {
            CacheType::Fifo(c) => c.touch(id, address),
            CacheType::Lru(c) => c.touch(id, address),
            CacheType::Sieve(c) => c.touch(id, address),
            CacheType::Random(c) => c.touch(id, address),
            CacheType::TreePlru(c) => c.touch(id, address),
        }
    }

    pub fn evict(&mut self) -> usize {
        match self {
            CacheType::Fifo(c) => c.evict(),
            CacheType::Lru(c) => c.evict(),
            CacheType::Sieve(c) => c.evict(),
            CacheType::Random(c) => c.evict(),
            CacheType::TreePlru(c) => c.evict(),
        }
    }

    pub fn name(&self) -> String {
        match self {
            CacheType::Fifo(c) => c.name(),
            CacheType::Lru(c) => c.name(),
            CacheType::Sieve(c) => c.name(),
            CacheType::Random(c) => c.name(),
            CacheType::TreePlru(c) => c.name(),
        }
    }

    pub fn is_eviction_set(&self, id: usize) -> bool {
        match self {
            CacheType::Fifo(c) => c.is_eviction_set(id),
            CacheType::Lru(c) => c.is_eviction_set(id),
            CacheType::Sieve(c) => c.is_eviction_set(id),
            CacheType::Random(c) => c.is_eviction_set(id),
            CacheType::TreePlru(c) => c.is_eviction_set(id),
        }
    }
}

impl<T, S> Cache<T, S>
where
    T: CacheLineMetadata<S>,
    S: CacheMetadata,
{
    pub fn new(assoc: usize) -> Self {
        let mut lines: CacheLines<T, S> = Vec::with_capacity(assoc);
        for _ in 0..assoc {
            lines.push(None);
        }
        let metadata = S::new(assoc);
        Self { lines, metadata }
    }

    pub fn find(&self, id: usize, addr: usize) -> Option<usize> {
        self.lines
            .iter()
            .position(|line| line.as_ref().is_some_and(|l| l.id == id && l.addr == addr))
    }

    pub fn is_full(&self) -> bool {
        !self.lines.iter().any(|line| line.is_none())
    }

    pub fn find_empty(&self) -> Option<usize> {
        self.lines.iter().position(|line| line.as_ref().is_none())
    }

    pub fn is_eviction_set(&self, id: usize) -> bool {
        self.lines
            .iter()
            .all(|line| line.as_ref().is_some_and(|l| l.id == id))
    }
}

// Empty metadata implementations
impl<S> CacheLineMetadata<S> for () {
    fn new(_: &mut S) -> Self {
        ()
    }

    fn touch(&mut self, _: &mut S) {}
}

impl CacheMetadata for () {
    fn new(_: usize) -> Self {
        ()
    }
}
