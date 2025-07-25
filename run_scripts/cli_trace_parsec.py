import subprocess
from concurrent.futures import ProcessPoolExecutor
import time

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
assocs = [16]
replacement_policies = [
    "sieve",
    "rr",
    "treeplru",
    "3tree",
    "rrip",
]

labels = []
commands = []

# Add FS checkpoint generation workloads
"""
# Checkpoint generation
build/ARM/gem5.opt --outdir=m5out/bbench \
./configs/deprecated/example/fs.py [fs.py options] \
--benchmark bbench-ics
"""
# for benchmark in benchmarks:
#     labels.append(
#         f"================================\n\
# SPEC 2017 TRACE CHECKPOINT GENERATION\n\
# Benchmark:     {benchmark}\n\n"
#     )
#
#     commands.append(
#         " ".join([
#             "gem5/build/X86/gem5.fast",
#             "--outdir=out/trace",
#             "run_scripts/bench/spec_trace_generate.py",
#             "--image benchmark/spec-2017/spec-2017-image/spec-2017",
#             "--size ref",
#             f"--benchmark {benchmark}",
#         ])
#     )
# p = subprocess.Popen("gem5/build")

# Add FS checkpoint restore workloads
"""
# Checkpoint restore
build/ARM/gem5.opt --outdir=m5out/bbench/capture_10M \
./configs/deprecated/example/fs.py [fs.py options] \
--cpu-type=arm_detailed --caches \
--elastic-trace-en --data-trace-file=deptrace.proto.gz --inst-trace-file=fetchtrace.proto.gz \
--mem-type=SimpleMemory \
--checkpoint-dir=m5out/bbench -r 0 --benchmark bbench-ics -I 10000000
"""
for assoc in assocs:
    for repl_policy in replacement_policies:
        for benchmark in benchmarks:
            labels.append(
                f"================================\n\
PARSEC TRACE CHECKPOINT RESTORE\n\
Benchmark:     {benchmark}\n\n"
            )

            commands.append(
                " ".join(
                    [
                        "gem5/build/X86/gem5.fast",
                        "run_scripts/bench/parsec_trace.py",
                        f"--outjson out/trace/{benchmark}",
                        f"--benchmark {benchmark}",
                        "--checkpoint-dir=out/trace/checkpt-parsec",
                        "-r 0",
                    ]
                )
            )

runs = list(zip(commands, labels))


def run_command_synchronous(command: str, label: str):
    print(label)
    print(command)
    p = subprocess.Popen(command, shell=True)
    p.wait()


start = time.perf_counter()

with ProcessPoolExecutor(max_workers=16) as executor:
    run_futures = [
        executor.submit(run_command_synchronous, run[0], run[1]) for run in runs
    ]

finish = time.perf_counter()
print(f"SPEC CPU finished tracing in {(finish - start):.2f} seconds")

# cpus = 4

# group_runs = []
# while len(runs) > 0:
# group_runs.append(runs[:num_threads])
# runs = runs[num_threads:]
#
# while len(group_runs) > 0:
# group_batch = group_runs[:num_thread_groups]
# group_runs = group_runs[num_thread_groups:]
# for group in group_runs:
#

# while runs:
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
