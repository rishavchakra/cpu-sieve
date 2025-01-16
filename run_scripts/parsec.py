import subprocess
from subprocess import Popen
from concurrent.futures import ThreadPoolExecutor
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
    # "lru",
    # "fifo",
    "rr",
    # "second-chance",
    "tree-plru",
    # "weighted-lru",
]

assocs = [
    8,
    16,
    4,
    2,
]

labels = []
commands = []

for assoc in assocs:
    for benchmark in benchmarks:
        for repl_policy in replacement_policies:
            labels.append(
                f"================================\n\
    PARSEC SIMULATION\n\
    Benchmark:     {benchmark}\n\
    Replacement Policy: {repl_policy}\n\
    Associativity:      {assoc}\n"
            )

            # If linux with KVM enabled: switch 'atomic' 7 lines down to 'kvm'
            commands.append(
                f"""gem5/build/X86/gem5.opt \
-d out/parsec/{benchmark}/{repl_policy}/{assoc} \
parsec/configs/run_parsec.py \
--kernel parsec/vmlinux-4.19.83 \
--disk parsec/disk-image/parsec/parsec-image/parsec \
--cpu atomic \
--size test \
--num_cpus 1 \
--benchmark {benchmark} \
-a {str(assoc)} \
-r {repl_policy}"""
            )

runs = zip(commands, labels)

with ThreadPoolExecutor(max_workers=6) as executor:
    for run in runs:
        print(run[1])
        future = executor.submit(run[0])

# cpus = 4
# while commands:
#     run_batch = runs[:cpus]
#     commands_batch = [run[0] for run in run_batch]
#     labels_batch = [run[1] for run in run_batch]
#     runs = runs[cpus:]
#     # batch = commands[:cpus]
#     # commands = commands[cpus:]
#     for label in labels_batch:
#         print(label)
#     procs = [subprocess.Popen(cmd, shell=True) for cmd in commands_batch]
#     for p in procs:
#         p.wait()
