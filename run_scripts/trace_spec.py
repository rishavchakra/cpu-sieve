import subprocess
from concurrent.futures import ProcessPoolExecutor
import time

benchmarks = [
    "503.bwaves_r",
    "507.cactuBSSN_r",
    "508.namd_r",
    "510.parest_r",
    "511.povray_r",
    "519.lbm_r",
    "521.wrf_r",
    "526.blender_r",
    "527.cam4_r",
    "538.imagick_r",
    "544.nab_r",
    "549.fotonik3d_r",
    "554.roms_r",
    "997.specrand_fr",
    # "603.bwaves_s",
    # "607.cactuBSSN_s",
    # "619.lbm_s",
    # "621.wrf_s",
    # "627.cam4_s",
    # "628.pop2_s",
    # "638.imagick_s",
    # "644.nab_s",
    # "649.fotonik3d_s",
    # "654.roms_s",
    "996.specrand_fs",
    "500.perlbench_r",
    "502.gcc_r",
    "505.mcf_r",
    "520.omnetpp_r",
    "523.xalancbmk_r",
    "525.x264_r",
    "531.deepsjeng_r",
    "541.leela_r",
    "548.exchange2_r",
    "557.xz_r",
    "999.specrand_ir",
    # "600.perlbench_s",
    # "602.gcc_s",
    # "605.mcf_s",
    # "620.omnetpp_s",
    # "623.xalancbmk_s",
    # "625.x264_s",
    # "631.deepsjeng_s",
    # "641.leela_s",
    # "648.exchange2_s",
    # "657.xz_s",
    "998.specrand_is",
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
for benchmark in benchmarks:
    labels.append(
        f"================================\n\
SPEC 2017 TRACE CHECKPOINT GENERATION\n\
Benchmark:     {benchmark}\n\n"
    )

    commands.append(
        " ".join([
            "gem5/build/X86/gem5.fast",
            "--outdir=out/trace",
            "run_scripts/bench/spec_trial.py",
            "--image benchmark/spec-2017/spec-2017-image/spec-2017",
            "--size ref",
            f"--benchmark {benchmark}",
        ])
    )

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
for benchmark in benchmarks:
    labels.append(
        f"================================\n\
SPEC 2017 TRACE CHECKPOINT RESTORE\n\
Benchmark:     {benchmark}\n\n"
    )

    commands.append(
        " ".join([
                     "gem5/build/X86/gem5.fast",
                     "--outdir=out/trace/capture",
                     "run_scripts/bench/spec_trial.py",
                    "--image benchmark/spec-2017/spec-2017-image/spec-2017",
                    "--size ref",
                    f"--benchmark {benchmark}",
                 ])
    )

runs = list(zip(commands, labels))

def run_command_synchronous(command: str, label: str):
    print(label)
    print(command)
    p = subprocess.Popen(command, shell=True)
    p.wait()

start = time.perf_counter()

with ProcessPoolExecutor(max_workers=16) as executor:
    run_futures = [executor.submit(run_command_synchronous, run[0], run[1]) for run in runs]

finish = time.perf_counter()
print(f'SPEC CPU finished tracing in {(finish - start):.2f} seconds')

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
