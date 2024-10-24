use algorithms::{Fifo, Sieve};
use cache::Cache;

mod algorithms;
mod cache;
mod patterns;

fn main() {
    println!("beep beep eviction set testing");
    let c = Cache::<Fifo>::new(8);
    if c.is_eviction_set(1) {
        println!("wahoo!");
    } else {
        println!("oops");
    }

}
