use crate::algorithms::{CacheLine, CacheSet};

pub struct Cache<T>
where
    T: CacheLine,
    Vec<Option<T>>: CacheSet<T>,
{
    lines: Vec<Option<T>>,
}

impl<T> Cache<T>
where
    T: CacheLine,
    Vec<Option<T>>: CacheSet<T>,
{
    pub fn new(assoc: usize) -> Self {
        let mut lines: Vec<Option<T>> = Vec::with_capacity(assoc);
        for _ in 0..assoc {
            lines.push(None);
        }
        Self { lines }
    }

    pub fn contains(&self, id: usize, addr: usize) -> bool {
        self.lines.iter().any(|line| {
            line.as_ref()
                .is_some_and(|l| l.get_id() == id && l.get_address() == addr)
        })
    }

    pub fn is_full(&self) -> bool {
        !self.lines.iter().any(|line| line.is_none())
    }

    pub fn is_eviction_set(&self, id: usize) -> bool {
        self.lines.iter().all(|line| match line {
            Some(l) => l.get_id() == id,
            None => false,
        })
    }

    pub fn touch(&mut self, id: usize, addr: usize) {
        self.lines.touch(id, addr)
    }

    pub fn evict(&mut self) -> usize {
        self.lines.evict()
    }
}
