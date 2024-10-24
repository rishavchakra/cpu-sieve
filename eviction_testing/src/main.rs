use access_patterns::AccessPattern;
use algorithms::{Fifo, Sieve};
use cache::Cache;

mod access_patterns;
mod algorithms;
mod cache;

#[derive(Copy, Clone)]
enum User {
    INIT = 0,
    VICTIM = 1,
    ATTACKER = 2,
}

fn main() {
    let mut c = Cache::<Fifo>::new(8);

    let access_pattern = access_patterns::Sequential::new(User::ATTACKER as usize, 8, 8);

    for access in access_pattern {
        println!("{:?}", access);
        c.touch(access.id, access.addr);

        if c.is_full() {
            println!("Cache full!");
        }

        if c.is_eviction_set(access.id) {
            println!("Eviction set!");
            break;
        }

        if access.num_access > 1000 {
            println!("Exceeded touch limit, eviction set never created");
            break;
        }
    }

    println!("Finished testing :)");
}
