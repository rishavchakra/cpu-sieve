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

labels: list[str] = []
commands: list[list[str]] = []

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
                [
                    "gem5/build/X86/gem5.fast",
                    f"-d out/parsec/{benchmark}/{repl_policy}/{assoc}",
                    "run_scripts/bench/parsec_trial.py",
                    "--kernel vmlinux-4.19.83",
                    "--disk benchmark/parsec/parsec-image",
                    "--cpu kvm",
                    "--size simsmall",
                    "--num_cpus 1",
                    f"--benchmark {benchmark}",
                    f"--assoc {str(assoc)}",
                    f"--repl {repl_policy}",
                ]
            )


def run_command_synchronous(command: list[str]):
    p = subprocess.Popen(command, shell=False)
    _ = p.wait()


runs = zip(commands, labels)

with ThreadPoolExecutor(max_workers=24) as executor:
    for run in runs:
        print(run[1])
        future = executor.submit(run_command_synchronous, run[0])

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
