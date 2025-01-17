import subprocess
from subprocess import Popen
from concurrent.futures import ThreadPoolExecutor
import os

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
    SPEC 2017 SIMULATION\n\
    Benchmark:     {benchmark}\n\
    Replacement Policy: {repl_policy}\n\
    Associativity:      {assoc}\n"
            )

            # If linux with KVM enabled: switch 'atomic' 7 lines down to 'kvm'
            # Old command
            """
            gem5/build/X86/gem5.opt \
            -d out/spec-cpu/{benchmark}/{repl_policy}/{assoc} \
            run_scripts/spec/run.py \
            --kernel ../vmlinux-4.19.83 \
            --disk benchmark/spec-2017/spec-2017-image/spec-2017 \
            --cpu kvm \
            --size test \
            --num_cpus 1 \
            --benchmark {benchmark} \
            --assoc {str(assoc)} \
            --repl {repl_policy}
            """

            commands.append(
                f"""gem5/build/X86/gem5.opt \
-d out/spec-cpu/ \
run_scripts/spec/run.py \
--image benchmark/spec-2017/spec-2017-image/spec-2017 \
--size ref \
--benchmark {benchmark} \
--assoc {str(assoc)} \
--repl {repl_policy}"""
            )

runs = list(zip(commands, labels))

# with ThreadPoolExecutor(max_workers=6) as executor:
    # for run in runs:
        # print(run[1])
        # future = executor.submit(run[0])

print("SPEC CPU finished simulating!")

cpus = 6
while runs:
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
