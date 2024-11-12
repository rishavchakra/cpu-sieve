use chrono::Local;
use std::fs::File;
use std::io::{BufWriter, Write};

pub struct CsvLogger {
    writer: BufWriter<File>,
}

impl CsvLogger {
    pub fn new() -> Self {
        let dt = Local::now();
        let time = format!("{}", dt.format("%Y-%m-%d-%H-%M-%S"));
        println!("Starting simulation at time {}", time);

        let filepath = format!("sim-results/{}.csv", time);
        let file = File::create_new(filepath).expect("ERROR: could not create results file");
        let mut writer = BufWriter::new(file);
        let _ = writer.write(b"Cache Type,Associativity,Evset Addresses,Access Pattern,Num Accesses\n");

        Self { writer }
    }

    pub fn log_evset(
        &mut self,
        cache_type: String,
        assoc: usize,
        evset_addrs: usize,
        access_pattern: String,
        num_accesses: usize,
    ) {
        let csv_line = format!(
            "{},{},{},{},{}\n",
            cache_type, assoc, evset_addrs, access_pattern, num_accesses
        );
        self.writer.write(csv_line.as_bytes()).unwrap();
    }
}
