use std::marker::PhantomData;

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

pub trait CacheTrait {
    fn touch(&mut self, id: usize, address: usize);

    fn evict(&mut self) -> usize;
}

pub trait CacheLineMetadata<S> {
    fn new(cache_metadata: &mut S) -> Self;

    fn touch(&mut self, cache_metadata: &mut S);
}

pub trait CacheMetadata {
    fn new(assoc: usize) -> Self;
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
        self.lines.iter().all(|line| match line {
            Some(l) => l.id == id,
            None => false,
        })
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
