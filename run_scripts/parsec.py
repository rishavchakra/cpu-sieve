import subprocess
from subprocess import Popen
from concurrent.futures import ProcessPoolExecutor
import os

benchmarks = [
    "blackscholes",
    "bodytrack",
    "canneal",
    "dedup",
    "facesim",
    "ferret",
    "fluidanimate",
    "freqmine",
    "raytrace",
    "streamcluster",
    "swaptions",
    "vips",
    "x264",
]

replacement_policies = [
    "sieve",
    # "tree-sieve",
    "lru",
    # "fifo",
    "rr",
    # "second-chance",
    "tree-plru",
    # "weighted-lru",
]

assocs = [
    8,
    4,
    16,
    2,
]

commands = []

for assoc in assocs:
    for benchmark in benchmarks:
        for repl_policy in replacement_policies:
            print(
                f"================================\n\
    PARSEC SIMULATION\n\
    Benchmark:     {benchmark}\n\
    Replacement Policy: {repl_policy}\n\
    Associativity:      {assoc}\n"
            )

            commands.append(
                f"""gem5/build/X86/gem5.opt \
-d out/parsec/{benchmark}/{repl_policy}/{assoc} \
parsec/configs/run_parsec.py \
--kernel parsec/vmlinux-4.19.83 \
--disk parsec/disk-image/parsec/parsec-image/parsec \
--cpu timing \
--size simsmall \
--num_cpus 1 \
--benchmark {benchmark} \
-a {str(assoc)} \
-r {repl_policy}"""
            )

cpus = 4
while commands:
    batch = commands[:cpus]
    commands = commands[cpus:]
    procs = [subprocess.Popen(i, shell=True) for i in batch]
    for p in procs:
        p.wait()
