use access_patterns::{Access, AccessPattern, AccessPatternType};
use algorithms::{FifoCache, LruCache, RandomCache, SieveCache, TreePlruCache};
use cache::CacheType;
use strum::IntoEnumIterator;

mod access_patterns;
mod algorithms;
mod cache;
mod logger;

const MAX_LOG_ASSOC: u32 = 5;
const MAX_EVSET_TOUCHES: usize = 10_000;
const RAND_INIT: bool = true;
const ACCESS_PATTERN: AccessPatternType = AccessPatternType::Random;
const NUM_TRIALS: usize = 256;

#[derive(Copy, Clone)]
enum User {
    INIT = 0,
    VICTIM = 1,
    ATTACKER = 2,
}

fn main() {
    let mut caches: Vec<CacheType>;

    let mut csv_log = logger::CsvLogger::new();

    for log_assoc in 0..MAX_LOG_ASSOC {
        let assoc = 2usize.pow(log_assoc);

        for pattern in AccessPatternType::iter() {
            for _ in 0..NUM_TRIALS {
                caches = vec![
                    CacheType::Fifo(FifoCache::new_random(assoc, User::INIT as usize)),
                    CacheType::Lru(LruCache::new_random(assoc, User::INIT as usize)),
                    CacheType::Sieve(SieveCache::new_random(assoc, User::INIT as usize)),
                    CacheType::Random(RandomCache::new_random(assoc, User::INIT as usize)),
                    CacheType::TreePlru(TreePlruCache::new_random(assoc, User::INIT as usize)),
                ];

                let mut cache_evsets: Vec<(CacheType, bool)> =
                    caches.into_iter().map(|c| (c, false)).collect();

                let access_pattern: Box<dyn Iterator<Item = Access>> =
                    match pattern {
                        AccessPatternType::Sequential => Box::new(
                            access_patterns::Sequential::new(User::ATTACKER as usize, assoc, assoc),
                        ),
                        AccessPatternType::Random => Box::new(access_patterns::Random::new(
                            User::ATTACKER as usize,
                            assoc,
                            assoc,
                        )),
                        AccessPatternType::Double => Box::new(access_patterns::Double::new(
                            User::ATTACKER as usize,
                            assoc,
                            assoc,
                        )),
                    };

                // Attacker touches
                for (access_ind, access) in access_pattern.enumerate() {
                    cache_evsets.iter_mut().for_each(|(cache, is_evset)| {
                        if !*is_evset {
                            cache.touch(access.id, access.addr);

                            if cache.is_eviction_set(access.id) || access_ind >= MAX_EVSET_TOUCHES {
                                csv_log.log_evset(
                                    cache.name(),
                                    assoc,
                                    assoc,
                                    pattern.name(),
                                    access.num_access + 1,
                                );

                                *is_evset = true;
                            }
                        }
                    });

                    if cache_evsets.iter().all(|(_, is_evset)| *is_evset) {
                        break;
                    }
                }
            }
            println!(
                "Finished simulating {}-way associative {} caches",
                assoc,
                pattern.name()
            );
        }
        println!(
            "Finished simulating caches with {}-way associativity",
            assoc
        );
    }
}
