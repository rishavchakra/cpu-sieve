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
    "rrip",
    "brrip",
    "nru",
]

assocs = [
    8,
    16,
    4,
    2,
]

labels: list[str] = []
commands: list[str] = []

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
                " ".join(
                    [
                        "gem5/build/X86/gem5.fast",
                        f"-d out/parsec/{benchmark}/{repl_policy}/{assoc}",
                        "run_scripts/bench/parsec_trial.py",
                        "--image benchmark/parsec/parsec-image",
                        "--size simsmall",
                        f"--benchmark {benchmark}",
                        f"--assoc {str(assoc)}",
                        f"--repl {repl_policy}",
                    ]
                )
            )


# def run_command_synchronous(command: str):
# print(run[1])
# print(run[0])
# p = subprocess.Popen(command, shell=False)
# _ = p.wait()


runs = list(zip(commands, labels))

# with ThreadPoolExecutor(max_workers=24) as executor:
# for run in runs:
# future = executor.submit(run_command_synchronous, run)

cpus = 8
while len(runs) > 0:
    run_batch = runs[:cpus]
    commands_batch = [run[0] for run in run_batch]
    labels_batch = [run[1] for run in run_batch]
    runs = runs[cpus:]
    # batch = commands[:cpus]
    # commands = commands[cpus:]
    for label in labels_batch:
        print(label)
    procs = [subprocess.Popen(cmd, shell=True) for cmd in commands_batch]
    for p in procs:
        p.wait()
