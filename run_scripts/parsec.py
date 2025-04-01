import subprocess
import asyncio
from subprocess import Popen
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Pool
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

replacement_policies = {
    "sieve": [],
    # "tree-sieve": [],
    # "lru": [],
    # "fifo": [],
    "rr": [],
    # "second-chance": [],
    "tree-plru": [],
    # "weighted-lru": [],
    "rrip": [],
    "brrip": [],
    "nru": [],
    "splru": [
        cold + hot + choice
        for cold in ["r", "l", "f"]
        for hot in ["r", "l", "f"]
        # for choice in ["h", "q", "e", "n"]
        for choice in ["n"]
    ],
}

assocs = [
    16,
    8,
    4,
    # 2,
]

labels: list[str] = []
commands: list[str] = []

for assoc in assocs:
    for benchmark in benchmarks:
        for repl_policy, repl_args in replacement_policies.items():
            labels.append(
                f"================================\n\
    PARSEC SIMULATION\n\
    Benchmark:     {benchmark}\n\
    Replacement Policy: {repl_policy}\n\
    Associativity:      {assoc}\n"
            )

            # If linux with KVM enabled: switch 'atomic' 7 lines down to 'kvm'
            command = [
                "gem5/gem5_build/X86/gem5.fast",
                f"-d out/parsec/{benchmark}/{repl_policy}/{assoc}",
                "run_scripts/bench/parsec_trial.py",
                "--image benchmark/parsec/parsec-image",
                "--size simsmall",
                f"--benchmark {benchmark}",
                f"--assoc {str(assoc)}",
                f"--repl {repl_policy}",
            ]
            if len(repl_args) > 0:
                for repl_arg in repl_args:
                    arg_command = command[:]
                    arg_command[
                        1
                    ] = f"-d out/parsec/{benchmark}/{repl_policy}-{repl_arg}/{assoc}"
                    arg_command.append(f"--variant {repl_arg}")
                    commands.append(" ".join(arg_command))
            else:
                commands.append(" ".join(command))


runs = list(zip(commands, labels))


# async def run_command(run: tuple[str, str], semaphore):
#     print(run[1])
#     async with semaphore:
#         run_args = run[0].split()
#         file = run_args[0]
#         proc = await asyncio.create_subprocess_exec(file, *run_args[1:])
#     print("Finished a simulation")
#     # print(run[0])
#     # p = subprocess.Popen(run[0], shell=False)
#     # rc = p.wait()


# async def main(runs: list[tuple[str, str]]):
#     batch_size = 36
#     semaphore = asyncio.Semaphore(value=batch_size)
#     async_cmds = []
#     for run in runs:
#         async_cmds.append(run_command(run, semaphore))
#     await asyncio.gather(*async_cmds)


# asyncio.run(main(runs))


# with ThreadPoolExecutor(max_workers=36) as executor:
#     _ = executor.map(run_command, runs)

# print("Finished all gem5 simulations!")
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
        _ = p.wait()
